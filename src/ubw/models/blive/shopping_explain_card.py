from ._base import *


class ShoppingExplainCardCommand(CommandModel):
    cmd: Literal['SHOPPING_EXPLAIN_CARD']
    data: dict  # 太复杂、一直在变、只是为了收米，谁爱写解析谁写
