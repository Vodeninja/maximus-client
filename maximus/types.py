from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from enum import Enum


class ChatType(Enum):
    DIALOG = "DIALOG"
    CHAT = "CHAT"


@dataclass
class User:
    id: int
    phone: Optional[int] = None
    name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    photo_id: Optional[int] = None
    base_url: Optional[str] = None
    options: List[str] = None
    
    def __post_init__(self):
        if self.options is None:
            self.options = []
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        if "contact" in data:
            contact = data.get("contact", {})
            names = contact.get("names", [{}])
            name_data = names[0] if names else {}
            return cls(
                id=contact.get("id", 0),
                phone=contact.get("phone"),
                name=name_data.get("name"),
                first_name=name_data.get("firstName"),
                last_name=name_data.get("lastName")
            )
        else:
            names = data.get("names", [{}])
            name_data = names[0] if names else {}
            return cls(
                id=data.get("id", 0),
                phone=data.get("phone"),
                name=name_data.get("name"),
                first_name=name_data.get("firstName"),
                last_name=name_data.get("lastName"),
                photo_id=data.get("photoId"),
                base_url=data.get("baseUrl"),
                options=data.get("options", [])
            )


@dataclass
class Message:
    id: str
    text: str
    sender: int
    time: int
    chat_id: int
    type: str = "USER"
    attaches: List[Dict[str, Any]] = None
    _client: Optional[Any] = None
    
    def __post_init__(self):
        if self.attaches is None:
            self.attaches = []
    
    @property
    def chat(self) -> Optional["Chat"]:
        if self._client:
            return self._client.get_chat(self.chat_id)
        return None
    
    @property
    def sender_user(self) -> Optional["User"]:
        if self._client:
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
    
    async def reply(self, text: str):
        if self._client:
            return await self._client.send_message(self.chat_id, text, reply_to=self.id)
        raise RuntimeError("Message not bound to client")
    
    async def reply_sticker(self, sticker_id: int):
        """Reply to this message with a sticker.
        
        Args:
            sticker_id (int): Sticker ID to send
            
        Returns:
            Optional[Message]: Reply message object
        """
        if self._client:
            return await self._client.send_sticker(self.chat_id, sticker_id, reply_to=self.id)
        raise RuntimeError("Message not bound to client")
    
    async def react(self, reaction: str = "👍"):
        """React to this message with an emoji.
        
        Args:
            reaction (str): Reaction emoji (default: "👍")
        """
        if self._client:
            return await self._client.send_reaction(self.chat_id, self.id, reaction)
        raise RuntimeError("Message not bound to client")
    
    async def edit(self, text: str):
        if self._client:
            return await self._client.edit_message(self.chat_id, self.id, text)
        raise RuntimeError("Message not bound to client")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], chat_id: int, client: Optional[Any] = None) -> "Message":
        return cls(
            id=data.get("id", ""),
            text=data.get("text", ""),
            sender=data.get("sender", 0),
            time=data.get("time", 0),
            chat_id=chat_id,
            type=data.get("type", "USER"),
            attaches=data.get("attaches", []),
            _client=client
        )


@dataclass
class Chat:
    id: int
    type: ChatType
    title: Optional[str] = None
    participants: Dict[int, int] = None
    last_message: Optional[Message] = None
    owner: Optional[int] = None
    created: Optional[int] = None
    modified: Optional[int] = None
    status: str = "ACTIVE"
    _client: Optional[Any] = None
    
    def __post_init__(self):
        if self.participants is None:
            self.participants = {}
    
    @property
    def display_name(self) -> str:
        if self.title:
            return self.title
        if self.type.value == "DIALOG" and self.participants:
            participant_ids = list(self.participants.keys())
            if participant_ids and self._client:
                user = self._client.get_user(participant_ids[0])
                if user and user.name:
                    return user.name
        return f"Chat {self.id}"
    
    async def send_message(self, text: str):
        if self._client:
            return await self._client.send_message(self.id, text)
        raise RuntimeError("Chat not bound to client")
    
    async def send_sticker(self, sticker_id: int):
        """Send a sticker to this chat.
        
        Args:
            sticker_id (int): Sticker ID to send
            
        Returns:
            Optional[Message]: Sent message object
        """
        if self._client:
            return await self._client.send_sticker(self.id, sticker_id)
        raise RuntimeError("Chat not bound to client")
    
    async def reply(self, message: Message, text: str):
        if self._client:
            return await self._client.send_message(self.id, text, reply_to=message.id)
        raise RuntimeError("Chat not bound to client")
    
    async def reply_sticker(self, message: Message, sticker_id: int):
        """Reply to a message with a sticker.
        
        Args:
            message (Message): Message to reply to
            sticker_id (int): Sticker ID to send
            
        Returns:
            Optional[Message]: Reply message object
        """
        if self._client:
            return await self._client.send_sticker(self.id, sticker_id, reply_to=message.id)
        raise RuntimeError("Chat not bound to client")
    
    async def react_to_message(self, message_id: str, reaction: str = "👍"):
        """React to a message in this chat.
        
        Args:
            message_id (str): ID of the message to react to
            reaction (str): Reaction emoji (default: "👍")
        """
        if self._client:
            return await self._client.send_reaction(self.id, message_id, reaction)
        raise RuntimeError("Chat not bound to client")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], client: Optional[Any] = None) -> "Chat":
        chat_type = ChatType(data.get("type", "DIALOG"))
        last_msg_data = data.get("lastMessage")
        last_message = None
        if last_msg_data:
            last_message = Message.from_dict(last_msg_data, data.get("id", 0), client)
        
        return cls(
            id=data.get("id", 0),
            type=chat_type,
            title=data.get("title"),
            participants=data.get("participants", {}),
            last_message=last_message,
            owner=data.get("owner"),
            created=data.get("created"),
            modified=data.get("modified"),
            status=data.get("status", "ACTIVE"),
            _client=client
        )

