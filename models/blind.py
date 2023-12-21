from datetime import datetime
from typing import Union

from pydantic import BaseModel, Field


class Blind(BaseModel):
    id: str = Field(None)
    channel: str = Field(None)
    name: str = Field(None)
    remote_id: str = Field(None)
    state:str = Field(None)
    online:bool = Field(None)
    rssi:str = Field(None)
    date_added: datetime = Field(None)
    is_in_discovery: bool = Field(False)
    discovery_stop: int = Field(0)
    last_stop_date: datetime = Field(None)
    last_ping: datetime = Field(None)


class BlindStates:
    STATE_STOPPED = "STOPPED"
    STATE_MOVING = "MOVING"
    STATE_DISCOVERY = "IN_DISCOVERY"
