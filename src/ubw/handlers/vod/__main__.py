import csv
import json
import warnings
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Annotated

import attrs
import typer


def CLASS(*v: str):
    # helper function, 'class' is a reserved word
    return {"class": ' '.join(vv for vv in v if vv)}


def DATA(data: dict[str, str]):
    return {f'data-{k}': v for k, v in data.items()}


app = typer.Typer()


@attrs.define
class Record:
    bvid: str
    duration: timedelta
    title: str
    cover: str
    demander_uname: str
    demander_uid: int
    demander_face: str
    owner_uname: str
    owner_uid: int
    owner_face: str
    vod_time: datetime
    original_text: str
    price: float
    tags: list[str]

    @property
    def broken(self):
        return False

    @property
    def over_time(self):
        return self.duration > timedelta(minutes=15)


@attrs.define
class BrokenRecord:
    bvid: str
    demander_uname: str
    demander_uid: int
    demander_face: str
    vod_time: datetime
    original_text: str
    price: float
    warning: str

    @property
    def broken(self):
        return True


def record_from_csv_dict(d: dict[str, str]) -> Record | BrokenRecord:
    if d['duration'] == '_broken':
        return BrokenRecord(
            bvid=d['bvid'],
            demander_uname=d['demander_uname'],
            demander_uid=int(d['demander_uid']),
            demander_face=d['demander_face'],
            price=float(d['price']),
            original_text=d['original_text'],
            vod_time=datetime.fromisoformat(d['vod_time']),
            warning=d['warning'],
        )
    return Record(
        bvid=d['bvid'],
        duration=timedelta(seconds=float(d['duration'])),
        title=d['title'],
        cover=d['cover'],
        demander_uname=d['demander_uname'],
        demander_uid=int(d['demander_uid']),
        demander_face=d['demander_face'],
        owner_uname=d['owner_uname'],
        owner_uid=int(d['owner_uid']),
        owner_face=d['owner_face'],
        vod_time=datetime.fromisoformat(d['vod_time']),
        original_text=d['original_text'],
        price=float(d['price']),
        tags=d['tags'].split('|'),
    )


def record_from_json_dict(d: dict[str, Any]) -> Record | BrokenRecord:
    if d.get('_broken', False):
        return BrokenRecord(
            bvid=d['bvid'],
            demander_uname=d['demander_uname'],
            demander_uid=d['demander_uid'],
            demander_face=d['demander_face'],
            price=d['price'],
            original_text=d['original_text'],
            vod_time=datetime.fromisoformat(d['vod_time']),
            warning=d['warning'],
        )
    return Record(
        bvid=d['bvid'],
        duration=timedelta(seconds=d['duration']),
        title=d['title'],
        cover=d['cover'],
        demander_uname=d['demander_uname'],
        demander_uid=d['demander_uid'],
        demander_face=d['demander_face'],
        owner_uname=d['owner_uname'],
        owner_uid=d['owner_uid'],
        owner_face=d['owner_face'],
        vod_time=datetime.fromisoformat(d['vod_time']),
        original_text=d['original_text'],
        price=d['price'],
        tags=d['tags'],
    )


def iter_record(path: Path, ext: str | None = None):
    if ext is None:
        ext = path.suffix
    if ext == '.jsonl':
        with path.open() as f:
            for line in f:
                yield record_from_json_dict(json.loads(line))
    elif ext == '.csv':
        with path.open(encoding='utf-8', newline='') as f:
            csv_reader = csv.DictReader(f)
            for row in csv_reader:
                yield record_from_csv_dict(row)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")


@app.command()
def total_time(path: Path | None = None):
    if path is None:
        path = Path(f"output/vod81004/{datetime.today().strftime("%Y%m%d")}.jsonl")
    assert path is not None
    total_seconds = 0
    for record in iter_record(path):
        if isinstance(record, BrokenRecord):
            pass
        duration = record.duration
        if duration > timedelta(minutes=15):
            warnings.warn(f"超时！已排除 {record.bvid}《{record.title}》 的时长 {duration}")
            continue
        total_seconds += duration
    print(f"总时长：{timedelta(seconds=total_seconds)}")


@app.command()
def fmt(
        path: Annotated[Path | None, typer.Argument()] = None,
        out_versions: Annotated[list[str], typer.Option("--out-version", "-t")] = None,
):
    if path is None:
        path = Path(f"output/vod81004/{datetime.today().strftime("%Y%m%d")}.jsonl")
    assert path is not None
    records = list(iter_record(path))
    from jinja2 import Environment, PackageLoader, select_autoescape
    env = Environment(
        loader=PackageLoader("ubw.handlers.vod"),
        autoescape=select_autoescape()
    )

    if out_versions is None:
        out_versions = ['2', ]
    for v in out_versions:
        template = env.get_template(f"v{v}.jinja")
        rendered = template.render(records=records)
        output = path.with_suffix(f".v{v}.html")
        assert output is not None
        with open(output, "w", encoding="utf-8") as f:
            f.write(rendered)


app()
