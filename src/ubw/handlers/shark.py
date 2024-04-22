import ast
import functools
import json
import logging
import pathlib

import aiofiles

from ._base import *
from ..models.blive.danmu_msg import parse_danmaku_info

logger = logging.getLogger('shark')


@functools.lru_cache()
def parse_expr(expr_str):
    return ast.parse(expr_str, mode='eval').body


def eval_on_cmd(expr, command: dict):
    match expr:
        case ast.BoolOp(values=[l, r], op=ast.And()):
            return eval_on_cmd(l, command) and eval_on_cmd(r, command)
        case ast.BoolOp(values=[l, r], op=ast.Or()):
            return eval_on_cmd(l, command) or eval_on_cmd(r, command)
        case ast.Compare(left=left, comparators=comparators, ops=ops):
            leftv = eval_on_cmd(left, command)
            for op, right in zip(ops, comparators):
                rightv = eval_on_cmd(right, command)
                match op:
                    case ast.Lt():
                        if not (leftv < rightv):
                            return False
                    case ast.LtE():
                        if not (leftv <= rightv):
                            return False
                    case ast.Gt():
                        if not (leftv > rightv):
                            return False
                    case ast.GtE():
                        if not (leftv >= rightv):
                            return False
                    case ast.NotEq():
                        if not (leftv != rightv):
                            return False
                    case ast.Eq():
                        if not (leftv == rightv):
                            return False
                    case _:
                        raise ValueError(f"unsupported Compare {op=}")
                leftv = rightv
            return True
        case ast.Attribute(attr=x_attr, value=x_value):
            v_value = eval_on_cmd(x_value, command)
            return v_value[x_attr]
        case ast.Subscript(value=x_value, slice=x_slice):
            v_value = eval_on_cmd(x_value, command)
            v_slice = eval_on_cmd(x_slice, command)
            return v_value[v_slice]
        case ast.Name(id=x_id):
            if x_id == '_':
                return command
            elif x_id == 'danmaku_info' and 'info' in command:
                return parse_danmaku_info(command['info'])
            # add builtins here
            return command.get(x_id, None)
        case ast.Constant(value=x_value):
            return x_value
        case ast.Slice(lower=x_lower, upper=x_upper, step=x_step):
            v_lower = None if x_lower is None else eval_on_cmd(x_lower, command)
            v_upper = None if x_upper is None else eval_on_cmd(x_upper, command)
            v_step = None if x_step is None else eval_on_cmd(x_step, command)
            return slice(v_lower, v_upper, v_step)
        case ast.BinOp(left=x_left, op=ast.BitOr(), right=ast.Name(id="json")):
            v_left = eval_on_cmd(x_left, command)
            return json.loads(v_left)
        case _:
            raise ValueError(f"unsupported expr\n{ast.dump(expr)}")


class SharkHandler(BaseHandler):
    cls: Literal['shark'] = 'shark'

    rule: str
    outf: pathlib.Path

    async def process_one(self, client, command):
        try:
            if eval_on_cmd(parse_expr(self.rule), command):
                async with aiofiles.open(self.outf, mode='a', encoding='utf-8') as afp:
                    await afp.write(json.dumps(command, indent=2, ensure_ascii=False))
        except Exception as e:
            logger.exception("exception", exc_info=e)
