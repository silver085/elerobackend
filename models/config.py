from typing import Union

from pydantic import BaseModel


class Config(BaseModel):
    id: Union[int, None] = None
    ssid_name: Union[str, None] = None
    ssid_password: Union[str, None] = None
    spibus: Union[int, None] = 0
    spics: Union[int, None] = 0
    speed: Union[int, None] = 0
    gdo0: Union[int, None] = 0
    gdo2: Union[int, None] = 0
    retransmit: Union[int, None] =0
