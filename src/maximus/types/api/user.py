from typing import Optional

from ..base import MaximusType


class User(MaximusType):
    id: int
    phone: Optional[int] = None
    name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    photo_id: Optional[int] = None
    base_url: Optional[str] = None