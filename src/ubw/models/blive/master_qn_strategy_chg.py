from ._base import *


class Data(BaseModel):
    mtime: datetime
    scatter: tuple[int, int]


class MasterQnStrategyChgCommand(CommandModel):
    cmd: Literal['master_qn_strategy_chg']
    data: Json[Data] | None = None
    mtime: datetime | None = None
    scatter: tuple[int, int] | None = None
