from ._base import *


class OnlineRankCountData(BaseModel):
    count: int

    @root_validator(pre=True)
    def online_count_is_count(cls, values):  # TODO: use validation_alias=AliasChoice(...) after pydantic v2.0
        if 'online_count' in values:
            values['count'] = values['online_count']
            del values['online_count']
        return values


class OnlineRankCountCommand(CommandModel):
    cmd: Literal['ONLINE_RANK_COUNT']
    data: OnlineRankCountData
