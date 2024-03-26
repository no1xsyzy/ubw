from pydantic import TypeAdapter, BaseModel, field_validator

# since it is testing
# noinspection PyProtectedMember
from ubw.models.blive._base import Color, strange_dict

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


def test_strange_dict():
    class Point(BaseModel):
        x: float
        y: float

    class Outer(BaseModel):
        p: Point

        validate_p = field_validator('p', mode='before')(strange_dict)

    outer = Outer.model_validate({'p': '{"x": 1.5, "y": 2.1}'})
    assert outer.p.x == 1.5
    assert outer.p.y == 2.1
