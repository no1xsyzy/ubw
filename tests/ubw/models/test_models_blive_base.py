from datetime import datetime

from pydantic import TypeAdapter, BaseModel, field_validator, ValidationError

# since it is testing
# noinspection PyProtectedMember
from ubw.models.blive._base import Color, strange_dict, convert_ns

TAC = TypeAdapter(Color)


def test_color():
    assert TAC.validate_python('#abc') == Color((0xAA, 0xBB, 0xCC))
    assert TAC.validate_python('#ABC') == Color((0xAA, 0xBB, 0xCC))
    assert TAC.validate_python('#aabbcc') == Color((0xAA, 0xBB, 0xCC))
    assert TAC.validate_python('#AABBCC') == Color((0xAA, 0xBB, 0xCC))
    assert TAC.validate_python('#aabbccdd') == Color((0xAA, 0xBB, 0xCC, 0xDD))
    assert TAC.validate_python('#AABBCCDD') == Color((0xAA, 0xBB, 0xCC, 0xDD))
    assert TAC.validate_python(0xAABBCC) == Color((0xAA, 0xBB, 0xCC))
    color = Color((0xAA, 0xBB, 0xCC))
    assert color.hashcolor == '#aabbcc'
    assert color.red == 0xAA
    assert color.green == 0xBB
    assert color.blue == 0xCC
    assert color.alpha is None

    try:
        Color(())
    except ValidationError as e:
        assert e.errors()[0]['msg'] == 'Value error, `()` is not a color'


def test_strange_dict():
    class Point(BaseModel):
        x: float = 1.0
        y: float = 1.0

    class Outer(BaseModel):
        p: Point

        validate_p = field_validator('p', mode='before')(strange_dict)

    outer = Outer.model_validate({'p': '{"x": 1.5, "y": 2.1}'})
    assert outer.p.x == 1.5
    assert outer.p.y == 2.1
    assert Outer.model_validate({'p': 'null'}).p.x == 1.0
    assert Outer.model_validate({'p': '{"incomplete json"'}).p.x == 1.0


def test_convert_ns():
    class NS(BaseModel):
        ns: datetime

        validate_ns = field_validator('ns', mode='before')(convert_ns)

    a = NS.model_validate({'ns': 1711418057123456789}).ns
    assert a.isoformat() == '2024-03-26T01:54:17.123457+00:00'

    b = NS.model_validate({'ns': 1711418057123}).ns
    assert b.isoformat() == '2024-03-26T01:54:17.123000+00:00'

    b = NS.model_validate({'ns': 1711418057}).ns
    assert b.isoformat() == '2024-03-26T01:54:17+00:00'
