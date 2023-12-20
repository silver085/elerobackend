from datetime import datetime
from typing import Union

from pydantic import BaseModel


class Blind(BaseModel):
    id: Union[str, None] = None
    name: Union[str, None] = None
    remote_id: Union[str, None] = None
    state: Union[str, None] = None
    online: Union[bool, None] = False
    rssi: Union[str, None] = None
    date_added: Union[datetime, None] = None
    is_in_discovery: Union[bool, None] = False
    discovery_stop: Union[int, None] = 0
    last_stop_date: Union[datetime, None] = None
