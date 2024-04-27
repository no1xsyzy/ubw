from typing import Annotated

from pydantic import Field, TypeAdapter

from .downloader import DownloaderApp
from .observer import ObserverApp
from .simple import SimpleApp

App = Annotated[SimpleApp | ObserverApp | DownloaderApp, Field(discriminator='cls')]

AppTypeAdapter = TypeAdapter[App](App)
