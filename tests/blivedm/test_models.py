from pydantic import parse_obj_as

from blivedm import models


def test_danmu_msg():
    c = parse_obj_as(
        models.AnnotatedCommandModel,
        {
            'cmd': 'DANMU_MSG',
            'info': [
                [
                    0, 4, 25, 14893055, 1676125072976, 1676124883, 0, "98095d8b", 0, 0, 5,
                    "#1453BAFF,#4C2263A2,#3353BAFF",
                    0,
                    "{}", "{}",
                    {
                        "mode": 0, "show_player_type": 0,
                        "extra": "{\"send_from_me\":false,\"mode\":0,\"color\":14893055,\"dm_type\":0,\"font_size\":25,\"player_mode\":4,\"show_player_type\":0,\"content\":\"？\",\"user_hash\":\"2550750603\",\"emoticon_unique\":\"\",\"bulge_display\":0,\"recommend_score\":0,\"main_state_dm_color\":\"\",\"objective_state_dm_color\":\"\",\"direction\":0,\"pk_direction\":0,\"quartet_direction\":0,\"anniversary_crowd\":0,\"yeah_space_type\":\"\",\"yeah_space_url\":\"\",\"jump_to_url\":\"\",\"space_type\":\"\",\"space_url\":\"\",\"animation\":{},\"emots\":null}"
                    },
                    {
                        "activity_identity": "", "activity_source": 0, "not_show": 0
                    }
                ],
                "？",
                [2351778, "橘枳橼", 0, 0, 0, 10000, 1, "#00D1F1"],
                [13, "降智了", "弱智光环", 8765806, 12478086, "", 0, 12478086, 12478086, 12478086, 0, 1, 531251],
                [23, 0, 5805790, ">50000", 2],
                ["", ""],
                0,
                3,
                None,
                {"ts": 1676125072, "ct": "1E12C41B"},
                0,
                0,
                None,
                None,
                0,
                105,
            ],
        }
    )
    assert isinstance(c, models.DanmakuCommand)


def test_super_chat_message():
    c = parse_obj_as(
        models.AnnotatedCommandModel,
        {
            'cmd': 'SUPER_CHAT_MESSAGE',
            'data': {
                "background_bottom_color": "#2A60B2",
                "background_color": "#EDF5FF",
                "background_color_end": "#405D85",
                "background_color_start": "#3171D2",
                "background_icon": "",
                "background_image": "https://i0.hdslb.com/bfs/live/a712efa5c6ebc67bafbe8352d3e74b820a00c13e.png",
                "background_price_color": "#7497CD",
                "color_point": 0.7,
                "dmscore": 120,
                "end_time": 1676124994,
                "gift": {
                    "gift_id": 12000,
                    "gift_name": "醒目留言",
                    "num": 1
                },
                "id": 6419133,
                "is_ranked": 1,
                "is_send_audit": 0,
                "medal_info": {
                    "anchor_roomid": 8765806,
                    "anchor_uname": "弱智光环",
                    "guard_level": 0,
                    "icon_id": 0,
                    "is_lighted": 1,
                    "medal_color": "#be6686",
                    "medal_color_border": 12478086,
                    "medal_color_end": 12478086,
                    "medal_color_start": 12478086,
                    "medal_level": 13,
                    "medal_name": "降智了",
                    "special": "",
                    "target_id": 531251
                },
                "message": "因为TCP的设计，上行和下行在接近极限的时候会相互卡住的，不过通常不会触到这个点",
                "message_font_color": "#A3F6FF",
                "message_trans": "",
                "price": 30,
                "rate": 1000,
                "start_time": 1676124934,
                "time": 59,
                "token": "30EB0101",
                "trans_mark": 0,
                "ts": 1676124935,
                "uid": 2351778,
                "user_info": {
                    "face": "https://i0.hdslb.com/bfs/face/757b6263c974aba03784fdbbe0d37c782f4c2045.jpg",
                    "face_frame": "https://i0.hdslb.com/bfs/live/80f732943cc3367029df65e267960d56736a82ee.png",
                    "guard_level": 3,
                    "is_main_vip": 1,
                    "is_svip": 0, "is_vip": 0, "level_color": "#5896de", "manager": 0, "name_color": "#00D1F1",
                    "title": "0", "uname": "橘枳橼", "user_level": 23
                }
            },
            'roomid': 81004
        }
    )
    assert isinstance(c, models.SuperChatCommand)
