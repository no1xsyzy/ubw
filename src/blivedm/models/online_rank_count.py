from ._base import *


class OnlineRankCountData(BaseModel):
    count: int

    @model_validator(mode='before')
    def online_count_is_count(cls, values):  # TODO: use validation_alias=AliasChoice(...)
        if 'online_count' in values:
            values['count'] = values['online_count']
            del values['online_count']
        return values


class OnlineRankCountCommand(CommandModel):
    cmd: Literal['ONLINE_RANK_COUNT']
    data: OnlineRankCountData
