from ._base import *


class UserTask(BaseModel):
    cur_progress: int
    cur_target: int
    done: int
    task_id: int


class UserTaskProgressData(BaseModel):
    count_down: int
    is_surplus: int
    linked_task: dict[str, UserTask] | None
    progress: int
    status: int
    target: int
    task_id: int


class UserTaskProgressCommand(CommandModel):
    cmd: Literal['USER_TASK_PROGRESS']
    data: UserTaskProgressData
