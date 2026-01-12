from typing import Annotated

from pydantic import Field, TypeAdapter

from .downloader import DownloaderApp
from .favsync import FavSyncApp
from .full_connect import FullConnectApp
from .observer import ObserverApp
from .simple import SimpleApp

App = Annotated[SimpleApp | ObserverApp | DownloaderApp | FullConnectApp | FavSyncApp, Field(discriminator='cls')]

AppTypeAdapter = TypeAdapter[App](App)
