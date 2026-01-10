from typing import Optional, Dict, Any, List, TYPE_CHECKING

from ..base import MaximusType

if TYPE_CHECKING:
    from maximus.types.api.chat import Chat
    from maximus.types.api.user import User
    from maximus.client import MaxClient


class Message(MaximusType):
    id: str
    text: str
    sender: int
    time: int
    chat_id: int
    type: str = "USER"
    attaches: List[Dict[str, Any]] = None
    
    def __post_init__(self) -> None:
        if self.attaches is None:
            object.__setattr__(self, 'attaches', [])
    
    @property
    def chat(self) -> Optional["Chat"]:
        if hasattr(self, '_client') and self._client:
            return self._client.get_chat(self.chat_id)
        return None
    
    @property
    def sender_user(self) -> Optional["User"]:
        if hasattr(self, '_client') and self._client:
            return self._client.get_user(self.sender)
        return None
    
    @property
    def sender_name(self) -> str:
        sender = self.sender_user
        if sender and sender.name:
            return sender.name
        return f"User {self.sender}"
    
    @property
    def chat_title(self) -> str:
        chat = self.chat
        if chat:
            return chat.display_name
        return self.sender_name
    
    async def reply(self, text: str) -> Optional["Message"]:
        if hasattr(self, '_client') and self._client:
            return await self._client.send_message(self.chat_id, text, reply_to=self.id)
        raise RuntimeError("Message not bound to client")
    
    async def reply_sticker(self, sticker_id: int) -> Optional["Message"]:
        if hasattr(self, '_client') and self._client:
            return await self._client.send_sticker(self.chat_id, sticker_id, reply_to=self.id)
        raise RuntimeError("Message not bound to client")
    
    async def react(self, reaction: str = "👍") -> None:
        if hasattr(self, '_client') and self._client:
            return await self._client.send_reaction(self.chat_id, self.id, reaction)
        raise RuntimeError("Message not bound to client")
    
    async def edit(self, text: str) -> Optional["Message"]:
        if hasattr(self, '_client') and self._client:
            return await self._client.edit_message(self.chat_id, self.id, text)
        raise RuntimeError("Message not bound to client")