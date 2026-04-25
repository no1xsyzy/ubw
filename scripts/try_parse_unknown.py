from json import JSONDecoder
from pathlib import Path

import typer

from ubw import models


def main(cmd_name: str):
    decoder = JSONDecoder()
    if cmd_name.startswith('XX_EXTRA_'):
        raise ValueError("Don't use this script to parse extra fields in unknown commands, must specify the cmd name.")
    jsonfile = Path(f"output/unknown_cmd/{cmd_name.upper()}.json")
    if not jsonfile.exists():
        raise ValueError(f"Could not find json file at {jsonfile}")
    jsons = jsonfile.read_text('utf-8')
    idx = 0
    while idx < len(jsons):
        if jsons[idx].isspace():
            idx += 1
            continue
        jj, idx = decoder.raw_decode(jsons, idx)
        m = models.BLIVE_ADAPTER.validate_python(jj)
        c = m.__class__
        if models.CommandModel not in c.mro() or c is models.CommandModel:
            raise ValueError(f"Parsed data expected to be subclasses of CommandModel, but got {c}")
        c: type[models.CommandModel]
        if c is not getattr(models, c.__name__, None):
            raise ValueError(f"Parsed data is all correct but not exported in models")
    print("all clear")


if __name__ == '__main__':
    typer.run(main)
