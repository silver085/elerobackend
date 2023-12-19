from typing import Union
from datetime import datetime

from pydantic import BaseModel


class User(BaseModel):
    id: Union[int, None] = None
    username: Union[str, None] = None
    password: Union[str, None] = None
    repeat_password: Union[str, None] = None
    email: Union[str, None] = None
    created_at: Union[datetime, None] = None
    is_admin: Union[bool, None] = None


class PassData(BaseModel):
    old_password: str
    password: str
    repeat_password: str
