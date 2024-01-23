from ._base import *


class OnlineRankV2Info(BaseModel):
    face: str
    guard_level: int
    rank: int
    uid: int
    uname: str


class OnlineRankV2Data(BaseModel):
    rank_type: str
    list: list[OnlineRankV2Info]

    @model_validator(mode='before')
    def online_list_is_list(cls, values):  # TODO: use validation_alias=AliasChoice(...)
        if 'online_list' in values:
            values['list'] = values['online_list']
            del values['online_list']
        return values


class OnlineRankV2Command(CommandModel):
    cmd: Literal['ONLINE_RANK_V2']
    data: OnlineRankV2Data
