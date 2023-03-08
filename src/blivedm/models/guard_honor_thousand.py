from ._base import *


class GuardHonorThousandData(BaseModel):
    add: list[int]
    del_: list[int] = Field(alias='del')


class GuardHonorThousandCommand(CommandModel):
    cmd: Literal['GUARD_HONOR_THOUSAND']
    data: GuardHonorThousandData
