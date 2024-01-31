from ._base import *


class ShoppingCartShowData(BaseModel):
    status: int


class ShoppingCartShowCommand(CommandModel):
    cmd: Literal['SHOPPING_CART_SHOW']
    data: ShoppingCartShowData
