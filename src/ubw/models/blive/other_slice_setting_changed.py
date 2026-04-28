from ._base import *


class Data(BaseModel):
    uid: int
    allow_other_edit: int = 0
    other_edit_level: int = 0


class OtherSliceSettingChangedData(BaseModel):
    data: Data


class OtherSliceSettingChangedCommand(CommandModel):
    cmd: Literal['OTHER_SLICE_SETTING_CHANGED']
    data: OtherSliceSettingChangedData
