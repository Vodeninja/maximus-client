from typing import Optional, Dict, TYPE_CHECKING

from ..base import MaximusType
from ..enums.chat_type import ChatType

if TYPE_CHECKING:
    from maximus.types.api.message import Message
    from maximus.types.api.user import User
    from maximus.client import MaxClient


class Chat(MaximusType):
    id: int
    type: ChatType
    title: Optional[str] = None
    participants: Dict[int, int] = None
    last_message: Optional["Message"] = None
    owner: Optional[int] = None
    created: Optional[int] = None
    modified: Optional[int] = None
    status: str = "ACTIVE"
    
    def __post_init__(self) -> None:
        if self.participants is None:
            object.__setattr__(self, 'participants', {})
    
    @property
    def display_name(self) -> str:
        if self.title:
            return self.title
        if self.type == ChatType.DIALOG and self.participants:
            participant_ids = list(self.participants.keys())
            if participant_ids and hasattr(self, '_client') and self._client:
                user = self._client.get_user(participant_ids[0])
                if user and user.name:
                    return user.name
        return f"Chat {self.id}"
    
    async def send_message(self, text: str) -> Optional["Message"]:
        if hasattr(self, '_client') and self._client:
            return await self._client.send_message(self.id, text)
        raise RuntimeError("Chat not bound to client")
    
    async def send_sticker(self, sticker_id: int) -> Optional["Message"]:
        if hasattr(self, '_client') and self._client:
            return await self._client.send_sticker(self.id, sticker_id)
        raise RuntimeError("Chat not bound to client")
    
    async def reply(self, message: "Message", text: str) -> Optional["Message"]:
        if hasattr(self, '_client') and self._client:
            return await self._client.send_message(self.id, text, reply_to=message.id)
        raise RuntimeError("Chat not bound to client")
    
    async def reply_sticker(self, message: "Message", sticker_id: int) -> Optional["Message"]:
        if hasattr(self, '_client') and self._client:
            return await self._client.send_sticker(self.id, sticker_id, reply_to=message.id)
        raise RuntimeError("Chat not bound to client")
    
    async def react_to_message(self, message_id: str, reaction: str = "👍") -> None:
        if hasattr(self, '_client') and self._client:
            return await self._client.send_reaction(self.id, message_id, reaction)
        raise RuntimeError("Chat not bound to client")