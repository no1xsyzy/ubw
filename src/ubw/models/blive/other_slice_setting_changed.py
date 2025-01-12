from ._base import *


class Data(BaseModel):
    uid: int
    allow_other_edit: int
    other_edit_level: int


class OtherSliceSettingChangedData(BaseModel):
    data: Data


class OtherSliceSettingChangedCommand(CommandModel):
    cmd: Literal['OTHER_SLICE_SETTING_CHANGED']
    data: OtherSliceSettingChangedData
