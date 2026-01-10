from typing import Dict, Any, Optional, TYPE_CHECKING
from ..types import User, Chat, Message, ChatType
from .interfaces import IDataMapper

if TYPE_CHECKING:
    from maximus.client import MaxClient


class DataMapper(IDataMapper):
    """Data mapper implementation."""
    
    def user_from_dict(self, data: Dict[str, Any]) -> User:
        """Map dict to User."""
        if "contact" in data:
            contact = data.get("contact", {})
            names = contact.get("names", [{}])
            name_data = names[0] if names else {}
            return User(
                id=contact.get("id", 0),
                phone=contact.get("phone"),
                name=name_data.get("name"),
                first_name=name_data.get("firstName"),
                last_name=name_data.get("lastName")
            )
        else:
            names = data.get("names", [{}])
            name_data = names[0] if names else {}
            return User(
                id=data.get("id", 0),
                phone=data.get("phone"),
                name=name_data.get("name"),
                first_name=name_data.get("firstName"),
                last_name=name_data.get("lastName"),
                photo_id=data.get("photoId"),
                base_url=data.get("baseUrl")
            )
    
    def message_from_dict(self, data: Dict[str, Any], chat_id: int, client: Optional["MaxClient"] = None) -> Message:
        """Map dict to Message."""
        message = Message(
            id=data.get("id", ""),
            text=data.get("text", ""),
            sender=data.get("sender", 0),
            time=data.get("time", 0),
            chat_id=chat_id,
            type=data.get("type", "USER"),
            attaches=data.get("attaches", [])
        )
        if client:
            object.__setattr__(message, '_client', client)
        return message
    
    def chat_from_dict(self, data: Dict[str, Any], client: Optional["MaxClient"] = None) -> Chat:
        """Map dict to Chat."""
        chat_type = ChatType(data.get("type", "DIALOG"))
        last_msg_data = data.get("lastMessage")
        last_message = None
        if last_msg_data:
            last_message = self.message_from_dict(last_msg_data, data.get("id", 0), client)
        
        chat = Chat(
            id=data.get("id", 0),
            type=chat_type,
            title=data.get("title"),
            participants=data.get("participants", {}),
            last_message=last_message,
            owner=data.get("owner"),
            created=data.get("created"),
            modified=data.get("modified"),
            status=data.get("status", "ACTIVE")
        )
        if client:
            object.__setattr__(chat, '_client', client)
        return chat