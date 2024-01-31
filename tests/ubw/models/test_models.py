from json import JSONDecoder
from pathlib import Path

from pydantic import TypeAdapter

from ubw import models


def test_exports_not_over():
    from ubw.models import blive, bilibili
    assert not set(blive.__all__) & set(bilibili.__all__)


def test_with_history():
    decoder = JSONDecoder()
    command_adapter = TypeAdapter(models.AnnotatedCommandModel)
    for jsonfile in Path("output/unknown_cmd").glob("*.json"):
        jsons = jsonfile.read_text('utf-8')
        idx = 0
        while idx < len(jsons):
            json, idx = decoder.raw_decode(jsons, idx)
            m = command_adapter.validate_python(json)
            c = m.__class__
            assert models.CommandModel in c.mro() and c is not models.CommandModel
