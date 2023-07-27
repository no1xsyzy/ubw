from ._base import *


class Data(BaseModel):
    status: int


class AnchorEcommerceStatusCommand(CommandModel):
    cmd: Literal['ANCHOR_ECOMMERCE_STATUS']
    data: Data
