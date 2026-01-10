from typing import Dict, List, Optional, Any
from ..types import Chat, User, Message, ChatType
from .interfaces import IDataMapper


class DataManager:
    """Data management for chats and users."""
    
    def __init__(self, mapper: IDataMapper) -> None:
        self._mapper = mapper
        self._chats: Dict[int, Chat] = {}
        self._users: Dict[int, User] = {}
        self._user: Optional[User] = None
    
    @property
    def user(self) -> Optional[User]:
        """Current user."""
        return self._user
    
    @property
    def chats(self) -> Dict[int, Chat]:
        """All chats."""
        return self._chats
    
    def get_chats(self) -> List[Chat]:
        """Get list of chats."""
        return list(self._chats.values())
    
    def get_chat(self, chat_id: int) -> Optional[Chat]:
        """Get specific chat."""
        chat = self._chats.get(chat_id)
        if chat and not hasattr(chat, '_client'):
            # Will be set by client
            pass
        return chat
    
    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self._users.get(user_id)
    
    def iter_chats(self):
        """Iterate over chats."""
        return iter(self._chats.values())
    
    def iter_users(self):
        """Iterate over users."""
        return iter(self._users.values())
    
    def set_current_user(self, user_data: Dict[str, Any]) -> None:
        """Set current user from data."""
        self._user = self._mapper.user_from_dict(user_data)
    
    def update_chats(self, chats_data: List[Dict[str, Any]], client: Optional[Any] = None) -> None:
        """Update chats from data."""
        for chat_data in chats_data:
            chat = self._mapper.chat_from_dict(chat_data, client=client)
            self._chats[chat.id] = chat
            
            if chat.type == ChatType.DIALOG and not chat.title:
                participant_ids = list(chat.participants.keys())
                for pid in participant_ids:
                    user = self.get_user(pid)
                    if user and user.name:
                        object.__setattr__(chat, 'title', user.name)
                        break
    
    def update_users(self, users_data: List[Dict[str, Any]]) -> List[User]:
        """Update users from data."""
        users = []
        for user_data in users_data:
            user = self._mapper.user_from_dict(user_data)
            self._users[user.id] = user
            users.append(user)
            
            # Update chat titles if needed
            if user.id in self._chats:
                chat = self._chats[user.id]
                if not chat.title and user.name:
                    object.__setattr__(chat, 'title', user.name)
        
        return users
    
    def create_message(self, message_data: Dict[str, Any], chat_id: int, client: Optional[Any] = None) -> Message:
        """Create message from data."""
        return self._mapper.message_from_dict(message_data, chat_id, client)