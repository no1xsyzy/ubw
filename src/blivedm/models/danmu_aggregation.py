from ._base import *


class DanmuAggregationData(BaseModel):
    activity_identity: int
    activity_source: int
    aggregation_cycle: int
    aggregation_icon: str
    aggregation_num: int
    broadcast_msg_type: int
    dmscore: int
    msg: str
    show_rows: int
    show_time: int
    timestamp: datetime


class DanmuAggregationCommand(CommandModel):
    cmd: Literal['DANMU_AGGREGATION']
    data: DanmuAggregationData
