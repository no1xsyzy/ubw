from ._base import *


class ShoppingBubble(BaseModel):
    name: str
    priority: int
    show_banner: int
    tag: str
    goods_list: list[int]


class ShoppingBubblesStyleData(BaseModel):
    bubbles_list: list[ShoppingBubble] | None = None
    checksum: str
    cycle_time: int
    goods_count: int
    interval_between_bubbles: int
    interval_between_queues: int


class ShoppingBubblesStyleCommand(CommandModel):
    cmd: Literal['SHOPPING_BUBBLES_STYLE']
    data: ShoppingBubblesStyleData
