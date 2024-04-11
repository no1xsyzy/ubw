from typing import Annotated, Union

from ._base import *
from .console import ConsoleUI
from .live import LiveUI
from .richy import Richy
from .web import Web

UI = Annotated[Union[ConsoleUI, LiveUI, Richy, Web], Field(discriminator='uic')]
