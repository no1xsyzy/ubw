from ._base import *


class ShoppingBubble(BaseModel):
    name: str
    priority: int
    show_banner: int = Field(validation_alias=AliasChoices('show_banner', 'showBanner'))
    tag: str
    goods_list: list[int] = Field(validation_alias=AliasChoices('goods_list', 'goodsList'))


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
