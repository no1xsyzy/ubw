from typing import Annotated

from pydantic import Field, TypeAdapter

from .downloader import DownloaderApp
from .full_connect import FullConnectApp
from .observer import ObserverApp
from .simple import SimpleApp

App = Annotated[SimpleApp | ObserverApp | DownloaderApp | FullConnectApp, Field(discriminator='cls')]

AppTypeAdapter = TypeAdapter[App](App)
