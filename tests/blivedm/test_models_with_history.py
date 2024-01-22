from json import JSONDecoder
from pathlib import Path

from pydantic.v1 import parse_obj_as

from blivedm import models

decoder = JSONDecoder()


def test_with_history():
    for jsonfile in Path("output/unknown_cmd").glob("*.json"):
        jsons = jsonfile.read_text('utf-8')
        idx = 0
        while idx < len(jsons):
            json, idx = decoder.raw_decode(jsons, idx)
            m = parse_obj_as(models.AnnotatedCommandModel, json)
            c = m.__class__
            assert models.CommandModel in c.mro() and c is not models.CommandModel
