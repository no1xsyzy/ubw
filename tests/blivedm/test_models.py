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
                    "#1453BAFF,#4C2263A2,#3353BAFF", 0, "{}", "{}",
                    {
                        "mode": 0, "show_player_type": 0,
                        "extra": "{\"send_from_me\":false,\"mode\":0,\"color\":14893055,\"dm_type\":0,\"font_size\":25,\"player_mode\":4,\"show_player_type\":0,\"content\":\"？\",\"user_hash\":\"2550750603\",\"emoticon_unique\":\"\",\"bulge_display\":0,\"recommend_score\":0,\"main_state_dm_color\":\"\",\"objective_state_dm_color\":\"\",\"direction\":0,\"pk_direction\":0,\"quartet_direction\":0,\"anniversary_crowd\":0,\"yeah_space_type\":\"\",\"yeah_space_url\":\"\",\"jump_to_url\":\"\",\"space_type\":\"\",\"space_url\":\"\",\"animation\":{},\"emots\":null}"
                    },
                    {"activity_identity": "", "activity_source": 0, "not_show": 0}
                ],
                "？",
                [2351778, "橘枳橼", 0, 0, 0, 10000, 1, "#00D1F1"],
                [13, "降智了", "弱智光环", 8765806, 12478086, "", 0, 12478086, 12478086, 12478086, 0, 1, 531251],
                [23, 0, 5805790, ">50000", 2],
                ["", ""],
                0, 3, None,
                {"ts": 1676125072, "ct": "1E12C41B"},
                0, 0, None, None, 0, 105,
            ],
        }
    )
    assert isinstance(c, models.DanmakuCommand)

    c = parse_obj_as(
        models.AnnotatedCommandModel,
        {
            'cmd': 'DANMU_MSG',
            'info': [
                [
                    0, 1, 25, 16777215, 1676564740293, -793983239, 0, '507d1d44', 0, 0, 0, '', 0, '{}', '{}',
                    {
                        'mode': 0, 'show_player_type': 0,
                        'extra': '{"send_from_me":false,"mode":0,"color":16777215,"dm_type":0,"font_size":25,"player_mode":1,"show_player_type":0,"content":"[妙]","user_hash":"1350376772","emoticon_unique":"","bulge_display":0,"recommend_score":1,"main_state_dm_color":"","objective_state_dm_color":"","direction":0,"pk_direction":0,"quartet_direction":0,"anniversary_crowd":0,"yeah_space_type":"","yeah_space_url":"","jump_to_url":"","space_type":"","space_url":"","animation":{},"emots":{"[妙]":{"emoticon_id":210,"emoji":"[妙]","descript":"[妙]","url":"http://i0.hdslb.com/bfs/live/08f735d950a0fba267dda140673c9ab2edf6410d.png","width":20,"height":20,"emoticon_unique":"emoji_210","count":1}},"is_audited":false}'
                    },
                    {'activity_identity': '', 'activity_source': 0, 'not_show': 0}
                ],
                '[妙]',
                [1753368819, '撸喵日常', 0, 0, 0, 10000, 1, ''],
                [11, '煤球怪', '踏雪寻梅3124', 666816, 9272486, '', 0, 12632256, 12632256, 12632256, 0, 0, 17393811],
                [1, 0, 9868950, '>50000', 0],
                ['', ''],
                0, 0, None,
                {'ts': 1676564740, 'ct': '9571FBCC'},
                0, 0, None, None, 0, 42
            ],
            'dm_v2': 'CPmNs4X9/////wESDzgxMDA0LTc5Mzk4MzIzORgBIBko////BzIINTA3ZDFkNDQ6BVvlppldQMXxrtjlMFD5jbOF/f////8BagB6YwoFW+WmmV0SWgoJZW1vamlfMjEwEklodHRwOi8vaTAuaGRzbGIuY29tL2Jmcy9saXZlLzA4ZjczNWQ5NTBhMGZiYTI2N2RkYTE0MDY3M2M5YWIyZWRmNjQxMGQucG5nMBQ4FJIBAA=='
        }
    )

    assert isinstance(c, models.DanmakuCommand)

    c = parse_obj_as(
        models.AnnotatedCommandModel,
        {
            "cmd": "DANMU_MSG",
            "info": [
                [
                    0,
                    1,
                    25,
                    16777215,
                    1677755311033,
                    1677742170,
                    0,
                    "98095d8b",
                    0,
                    0,
                    0,
                    "",
                    0,
                    "{}",
                    "{}",
                    {
                        "mode": 0,
                        "show_player_type": 0,
                        "extra": "{\"send_from_me\":false,\"mode\":0,\"color\":16777215,\"dm_type\":0,\"font_size\":25,\"player_mode\":1,\"show_player_type\":0,\"content\":\"test\",\"user_hash\":\"2550750603\",\"emoticon_unique\":\"\",\"bulge_display\":0,\"recommend_score\":3,\"main_state_dm_color\":\"\",\"objective_state_dm_color\":\"\",\"direction\":0,\"pk_direction\":0,\"quartet_direction\":0,\"anniversary_crowd\":0,\"yeah_space_type\":\"\",\"yeah_space_url\":\"\",\"jump_to_url\":\"\",\"space_type\":\"\",\"space_url\":\"\",\"animation\":{},\"emots\":null,\"is_audited\":false}"
                    },
                    {
                        "activity_identity": "",
                        "activity_source": 0,
                        "not_show": 0
                    }
                ],
                "test",
                [
                    2351778,
                    "\u6a58\u67b3\u6a7c",
                    0,
                    0,
                    0,
                    10000,
                    1,
                    ""
                ],
                [
                    14,
                    "\u964d\u667a\u4e86",
                    "\u5f31\u667a\u5149\u73af",
                    8765806,
                    12478086,
                    "",
                    0,
                    12478086,
                    12478086,
                    12478086,
                    0,
                    1,
                    531251
                ],
                [
                    23,
                    0,
                    5805790,
                    ">50000",
                    0
                ],
                [
                    "title-634-1",
                    "title-634-1"
                ],
                0,
                0,
                None,
                {
                    "ts": 1677755311,
                    "ct": "2202F6FD"
                },
                0,
                0,
                None,
                None,
                0,
                210
            ],
            "dm_v2": ""
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


def test_live_multi_view_change():
    c = parse_obj_as(
        models.AnnotatedCommandModel,
        {
            'cmd': 'LIVE_MULTI_VIEW_CHANGE',
            'data': {
                'scatter': {
                    'max': 120,
                    'min': 5
                }
            }
        }
    )
    assert isinstance(c, models.LiveMultiViewChangeCommand)


def test_anchor_lot_start():
    c = parse_obj_as(
        models.AnnotatedCommandModel,
        {
            'cmd': 'ANCHOR_LOT_START',
            'data': {
                'asset_icon': 'https://i0.hdslb.com/bfs/live/627ee2d9e71c682810e7dc4400d5ae2713442c02.png',
                'asset_icon_webp': 'https://i0.hdslb.com/bfs/live/b47453a0d42f30673b6d030159a96d07905d677a.webp',
                'award_image': '',
                'award_name': '白象方便面整箱',
                'award_num': 1,
                'award_type': 0,
                'cur_gift_num': 0,
                'current_time': 1677154113,
                'danmu': '不是白象我不吃',
                'danmu_new': [{
                    'danmu': '不是白象我不吃',
                    'danmu_view': '',
                    'reject': False
                }],
                'danmu_type': 0,
                'gift_id': 0,
                'gift_name': '',
                'gift_num': 1,
                'gift_price': 0,
                'goaway_time': 180,
                'goods_id': -99998,
                'id': 3940775,
                'is_broadcast': 1,
                'join_type': 0,
                'lot_status': 0,
                'max_time': 300,
                'require_text': '至少成为主播的舰长',
                'require_type': 3,
                'require_value': 3,
                'room_id': 81004,
                'send_gift_ensure': 0,
                'show_panel': 1,
                'start_dont_popup': 0,
                'status': 1,
                'time': 299,
                'url': 'https://live.bilibili.com/p/html/live-lottery/anchor-join.html?is_live_half_webview=1&hybrid_biz=live-lottery-anchor&hybrid_half_ui=1,5,100p,100p,000000,0,30,0,0,1;2,5,100p,100p,000000,0,30,0,0,1;3,5,100p,100p,000000,0,30,0,0,1;4,5,100p,100p,000000,0,30,0,0,1;5,5,100p,100p,000000,0,30,0,0,1;6,5,100p,100p,000000,0,30,0,0,1;7,5,100p,100p,000000,0,30,0,0,1;8,5,100p,100p,000000,0,30,0,0,1',
                'web_url': 'https://live.bilibili.com/p/html/live-lottery/anchor-join.html'
            }
        }

    )
    assert isinstance(c, models.AnchorLotStartCommand)


def test_anchor_lot_award():
    c = parse_obj_as(
        models.AnnotatedCommandModel,
        {
            'cmd': 'ANCHOR_LOT_AWARD',
            'data': {
                'award_dont_popup': 1,
                'award_image': '',
                'award_name': '白象方便面整箱',
                'award_num': 1,
                'award_type': 0,
                'award_users': [{
                    'uid': 1728860,
                    'uname': '街巷角落の黑猫',
                    'face': 'https://i2.hdslb.com/bfs/face/fd3055766c289a77d83d036457a8f886a70bbbed.jpg',
                    'level': 46,
                    'color': 16746162,
                    'num': 1
                }],
                'id': 3940775,
                'lot_status': 2,
                'url': 'https://live.bilibili.com/p/html/live-lottery/anchor-join.html?is_live_half_webview=1&hybrid_biz=live-lottery-anchor&hybrid_half_ui=1,5,100p,100p,000000,0,30,0,0,1;2,5,100p,100p,000000,0,30,0,0,1;3,5,100p,100p,000000,0,30,0,0,1;4,5,100p,100p,000000,0,30,0,0,1;5,5,100p,100p,000000,0,30,0,0,1;6,5,100p,100p,000000,0,30,0,0,1;7,5,100p,100p,000000,0,30,0,0,1;8,5,100p,100p,000000,0,30,0,0,1',
                'web_url': 'https://live.bilibili.com/p/html/live-lottery/anchor-join.html'
            }
        }
    )
    assert isinstance(c, models.AnchorLotAwardCommand)


def test_anchor_lot_end():
    c = parse_obj_as(
        models.AnnotatedCommandModel,
        {
            'cmd': 'ANCHOR_LOT_END',
            'data': {
                'id': 3940879
            }
        }
    )
    assert isinstance(c, models.AnchorLotEndCommand)


def test_anchor_lot_checkstatus():
    c = parse_obj_as(
        models.AnnotatedCommandModel,
        {
            'cmd': 'ANCHOR_LOT_CHECKSTATUS',
            'data': {
                'id': 3941001,
                'status': 4,
                'uid': 1521415
            }
        }
    )
    assert isinstance(c, models.AnchorLotCheckStatusCommand)


def test_widget_gift_star_process():
    c = parse_obj_as(
        models.AnnotatedCommandModel,
        {
            'cmd': 'WIDGET_GIFT_STAR_PROCESS',
            'data': {
                'start_date': 20230213,
                'process_list': [{
                    'gift_id': 32609,
                    'gift_img': 'https://s1.hdslb.com/bfs/live/15313516b3ec0875d67130f18c0a53c582e76531.png',
                    'gift_name': '礼物星球',
                    'completed_num': 21,
                    'target_num': 100
                },
                    {
                        'gift_id': 32611,
                        'gift_img': 'https://s1.hdslb.com/bfs/live/d157e6ded1e472f2788e6826f34398e065a0881a.png',
                        'gift_name': '礼物星球',
                        'completed_num': 14,
                        'target_num': 60
                    },
                    {
                        'gift_id': 32612,
                        'gift_img': 'https://s1.hdslb.com/bfs/live/dfaa7627f8aebccfb3a680dfd940ff7c1d1a341e.png',
                        'gift_name': '礼物星球',
                        'completed_num': 0,
                        'target_num': 2
                    }],
                'finished': False,
                'ddl_timestamp': 1676822400,
                'version': 1676486693573,
                'reward_gift': 32268,
                'reward_gift_img': 'https://s1.hdslb.com/bfs/live/7ca35670d343096c4bd9cd6d5491aa8a5305f82c.png',
                'reward_gift_name': '礼物星球'
            }
        }
    )
    assert isinstance(c, models.WidgetGiftStarProcessCommand)


def test_watched_change():
    c = parse_obj_as(
        models.AnnotatedCommandModel,
        {
            'cmd': 'WATCHED_CHANGE',
            'data': {
                'num': 122,
                'text_small': '122',
                'text_large': '122人看过'
            }
        }
    )

    assert isinstance(c, models.WatchedChangeCommand)


def test_notice_msg():
    c = parse_obj_as(
        models.AnnotatedCommandModel,
        {
            'cmd': 'NOTICE_MSG',
            'id': 742,
            'name': '3D小电视飞船专用',
            'full': {
                'head_icon': 'https://i0.hdslb.com/bfs/live/3ac21ee1dc5ea72e5b310c9cddcd6c9bc746d8c8.gif',
                'tail_icon': 'https://i0.hdslb.com/bfs/live/822da481fdaba986d738db5d8fd469ffa95a8fa1.webp',
                'head_icon_fa': 'https://i0.hdslb.com/bfs/live/3ac21ee1dc5ea72e5b310c9cddcd6c9bc746d8c8.gif',
                'tail_icon_fa': 'https://i0.hdslb.com/bfs/live/38cb2a9f1209b16c0f15162b0b553e3b28d9f16f.png',
                'head_icon_fan': 1,
                'tail_icon_fan': 4,
                'background': '#6097FFFF',
                'color': '#FFFFFF',
                'highlight': '#FFE600', 'time': 15
            },
            'half': {
                'head_icon': 'https://i0.hdslb.com/bfs/live/3ac21ee1dc5ea72e5b310c9cddcd6c9bc746d8c8.gif',
                'tail_icon': '',
                'background': '#6097FFFF',
                'color': '#FFFFFFFF',
                'highlight': '#FFE600',
                'time': 15
            },
            'side': {
                'head_icon': '',
                'background': '',
                'color': '',
                'highlight': '',
                'border': ''
            },
            'roomid': 26223227,
            'real_roomid': 26223227,
            'msg_common': '<%叭个毕加索%>投喂<%阿斯忒芮雪%>1个小电视飞船，向着浩瀚星辰出发！',
            'msg_self': '<%叭个毕加索%>投喂<%阿斯忒芮雪%>1个小电视飞船，向着浩瀚星辰出发！',
            'link_url': 'https://live.bilibili.com/26223227?broadcast_type=0&is_room_feed=1&from=28003&extra_jump_from=28003&live_lottery_type=1',
            'msg_type': 2,
            'shield_uid': -1,
            'business_id': '32122',
            'scatter': {'min': 0, 'max': 0},
            'marquee_id': '',
            'notice_type': 0
        }
    )

    assert isinstance(c, models.NoticeMsgCommand)

    c= parse_obj_as(
        models.AnnotatedCommandModel,
        {
            "cmd": "NOTICE_MSG",
            "id": 505,
            "name": "\u5927\u4e71\u6597\u8fde\u80dc\u4eba\u6c14\u7ea2\u5305",
            "full": {
                "head_icon": "https://i0.hdslb.com/bfs/live/ab106f494f4cc0c94fb78ed46144c72f6db000f6.webp",
                "tail_icon": "https://i0.hdslb.com/bfs/live/822da481fdaba986d738db5d8fd469ffa95a8fa1.webp",
                "head_icon_fa": "https://i0.hdslb.com/bfs/live/ab106f494f4cc0c94fb78ed46144c72f6db000f6.webp",
                "tail_icon_fa": "https://i0.hdslb.com/bfs/live/38cb2a9f1209b16c0f15162b0b553e3b28d9f16f.png",
                "head_icon_fan": 1,
                "tail_icon_fan": 4,
                "background": "#b6272b",
                "color": "#FFFFFFFF",
                "highlight": "#FDFF2FFF",
                "time": 15
            },
            "half": {
                "head_icon": "https://i0.hdslb.com/bfs/live/ab106f494f4cc0c94fb78ed46144c72f6db000f6.webp",
                "tail_icon": "",
                "background": "#b6272b",
                "color": "#FFFFFFFF",
                "highlight": "#FDFF2FFF",
                "time": 15
            },
            "side": {
                "head_icon": "",
                "background": "",
                "color": "",
                "highlight": "",
                "border": ""
            },
            "roomid": 23703544,
            "real_roomid": 23703544,
            "msg_common": "<%\u5f71\u6f5eKagami%>\u7684\u76f4\u64ad\u95f4\u53d1\u653e\u4e86\u4ef7\u503c<%100\u5143%>\u7684\u7ea2\u5305\uff0c\u5feb\u6765\u62a2\u9e2d\uff01",
            "msg_self": "\u606d\u559c<%\u5f71\u6f5eKagami%>\u83b7\u5f97\u5927\u4e71\u6597\u8fde\u80dc\u5956\u52b1\uff0c\u76f4\u64ad\u95f4\u53d1\u653e\u4ef7\u503c<%100\u5143%>\u7684\u7ea2\u5305\uff0c\u5feb\u6765\u62a2\u9e2d\uff01",
            "link_url": "https://live.bilibili.com/23703544?broadcast_type=0&is_room_feed=1&from=28003&extra_jump_from=28003&live_lottery_type=1",
            "msg_type": 2,
            "shield_uid": -1,
            "business_id": "19",
            "scatter": {
                "min": 0,
                "max": 0
            },
            "marquee_id": "",
            "notice_type": 0
        }
    )

    assert isinstance(c, models.NoticeMsgCommand)
