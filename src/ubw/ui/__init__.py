from typing import Annotated, Union

from ._base import *
from .console import ConsoleUI
from .live import LiveUI
from .richy import Richy

UI = Annotated[Union[ConsoleUI, LiveUI, Richy], Field(discriminator='uic')]
