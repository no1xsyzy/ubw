import json
from json import JSONDecoder
from pathlib import Path

from pydantic import TypeAdapter

from ubw import models

COMMAND_ADAPTER = TypeAdapter(models.AnnotatedCommandModel)


def test_exports_not_over():
    from ubw.models import blive, bilibili
    assert not set(blive.__all__) & set(bilibili.__all__)


def test_with_history():
    decoder = JSONDecoder()
    for jsonfile in Path("output/unknown_cmd").glob("*.json"):
        jsons = jsonfile.read_text('utf-8')
        idx = 0
        while idx < len(jsons):
            if jsons[idx].isspace():
                idx += 1
                continue
            jj, idx = decoder.raw_decode(jsons, idx)
            m = COMMAND_ADAPTER.validate_python(jj)
            c = m.__class__
            assert models.CommandModel in c.mro() and c is not models.CommandModel


def test_summary_guard_achievement_room():
    c = COMMAND_ADAPTER.validate_python({
        'cmd': 'GUARD_ACHIEVEMENT_ROOM',
        'data': {
            'anchor_basemap_url': '<anchor_basemap_url>',
            'anchor_guard_achieve_level': 1,
            'anchor_modal': {
                'first_line_content': '<first_line_content>',
                'highlight_color': '#AABBCC',
                'second_line_content': '<second_line_content>',
                'show_time': 1,
            },
            'app_basemap_url': '<app_basemap_url>',
            'current_achievement_level': 42,
            'dmscore': 1,
            'event_type': 1,
            'face': '<face>',
            'first_line_content': '<first_line_content>',
            'first_line_highlight_color': '<first_line_highlight_color>',
            'first_line_normal_color': '<first_line_normal_color>',
            'headmap_url': '<headmap_url>',
            'is_first': True,
            'is_first_new': True,
            'room_id': 1,
            'second_line_content': '<second_line_content>',
            'second_line_highlight_color': '<second_line_highlight_color>',
            'second_line_normal_color': '<second_line_normal_color>',
            'show_time': 1,
            'web_basemap_url': '<web_basemap_url>',
        }
    })

    summary = c.summarize()

    assert summary.msg == f"<first_line_content><second_line_content> (level=42)"


def test_summary_entry_effect():
    data = {
        'id': 1,
        'uid': 1,
        'target_id': 1,
        'mock_effect': 1,
        'face': '<face>',
        'privilege_type': 1,
        'copy_writing': '<copy_writing>',
        'copy_color': '#AABBCC',
        'priority': 1,
        'basemap_url': '<basemap_url>',
        'show_avatar': 1,
        'effective_time': 1,
        'web_basemap_url': '<web_basemap_url>',
        'web_effective_time': 1,
        'web_effect_close': 1,
        'web_close_time': 1,
        'business': 1,
        'copy_writing_v2': '<copy_writing_v2>',
        'icon_list': [],
        'max_delay_time': 1,
        'trigger_time': 1,
        'identities': 1,
        'effect_silent_time': 1,
        'effective_time_new': 1.1,
        'web_dynamic_url_webp': '<web_dynamic_url_webp>',
        'web_dynamic_url_apng': '<web_dynamic_url_apng>',
        'mobile_dynamic_url_webp': '<mobile_dynamic_url_webp>',
        'highlight_color': '#AABBCC',
        'wealthy_info': {
            'uid': 1,
            'level': 1,
            'level_total_score': 1,
            'cur_score': 1,
            'upgrade_need_score': 1,
            'status': 1,
            'dm_icon_key': '<dm_icon_key>',
        },
        'new_style': 1,
        'is_mystery': False,
        'uinfo': {
            'uid': 1,
            'base': {
                'name': '<name>',
                'face': '<face>',
                'name_color': '#AABBCC',
                'is_mystery': False,
            }
        },
    }

    s1 = COMMAND_ADAPTER.validate_python({
        'cmd': 'ENTRY_EFFECT',
        'data': data,
    }).summary()

    s2 = COMMAND_ADAPTER.validate_python({
        'cmd': 'ENTRY_EFFECT_MUST_RECEIVE',
        'data': data,
    }).summary()

    assert s1.msg == s2.msg == "<copy_writing>"


def test_danmu_msg():
    # deserialize without medal

    with open(Path(__file__).parent / 'danmu_msg.json') as f:
        j = json.load(f)

    c = COMMAND_ADAPTER.validate_python(j)
    s = c.summarize()

    assert s.msg == "......"

    # re-deserialize

    with open(Path(__file__).parent / 'danmu_msg2.json') as f:
        j = json.load(f)

    c = COMMAND_ADAPTER.validate_python(j)
    s = c.summarize()

    assert s.msg == "。"
