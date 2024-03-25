from typing import Annotated

from pydantic import Field, TypeAdapter

from .observer import ObserverApp
from .simple import SimpleApp

App = Annotated[SimpleApp | ObserverApp, Field(discriminator='cls')]

AppTypeAdapter = TypeAdapter[App](App)
