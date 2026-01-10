from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, Callable
from .constants import DEFAULT_CHATS_COUNT


class IConnection(ABC):
    """Interface for connection implementations."""
    
    @abstractmethod
    async def connect(self) -> None:
        """Connect to the service."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the service."""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connected."""
        pass
    
    @abstractmethod
    def register_event_handler(self, event: str, handler: Callable) -> None:
        """Register internal event handler."""
        pass
    
    @abstractmethod
    async def send_message(self, chat_id: int, text: str, reply_to: Optional[str] = None) -> int:
        """Send a message."""
        pass
    
    @abstractmethod
    async def send_sticker(self, chat_id: int, sticker_id: int, reply_to: Optional[str] = None) -> int:
        """Send a sticker."""
        pass
    
    @abstractmethod
    async def send_reaction(self, chat_id: int, message_id: str, reaction_type: str, reaction_id: str) -> int:
        """Send a reaction."""
        pass
    
    @abstractmethod
    async def edit_message(self, chat_id: int, message_id: str, text: str) -> int:
        """Edit a message."""
        pass
    
    @abstractmethod
    async def delete_message(self, chat_id: int, message_id: str) -> int:
        """Delete a message."""
        pass
    
    @abstractmethod
    async def send_auth_start(self, phone: str, language: str = "ru") -> int:
        """Start authentication."""
        pass
    
    @abstractmethod
    async def send_auth_code(self, token: str, verify_code: str) -> int:
        """Send auth code."""
        pass
    
    @abstractmethod
    async def send_auth_token(self, token: str, interactive: bool = False, chats_count: int = DEFAULT_CHATS_COUNT) -> int:
        """Send auth token."""
        pass
    
    @abstractmethod
    async def send_events(self, events: List[Dict[str, Any]]) -> int:
        """Send events."""
        pass
    
    @abstractmethod
    async def send_get_chats(self, chat_ids: List[int]) -> int:
        """Get chats."""
        pass
    
    @abstractmethod
    async def send_get_contacts(self, contact_ids: List[int]) -> int:
        """Get contacts."""
        pass


class ISessionManager(ABC):
    """Interface for session management."""
    
    @abstractmethod
    async def load(self) -> None:
        """Load session data."""
        pass
    
    @abstractmethod
    async def save(self) -> None:
        """Save session data."""
        pass
    
    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """Get session value."""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """Set session value."""
        pass
    
    @abstractmethod
    def get_all(self) -> Dict[str, Any]:
        """Get all session data."""
        pass


class IEventDispatcher(ABC):
    """Interface for event dispatching."""
    
    @abstractmethod
    def on(self, event_type: str) -> Callable:
        """Decorator for event handlers."""
        pass
    
    @abstractmethod
    def add_event_handler(self, event_name: str, handler: Callable) -> None:
        """Add event handler."""
        pass
    
    @abstractmethod
    def remove_event_handler(self, event_name: str, handler: Callable) -> None:
        """Remove event handler."""
        pass
    
    @abstractmethod
    async def dispatch_event(self, event_name: str, *args, **kwargs) -> None:
        """Dispatch event to handlers."""
        pass


class IDataMapper(ABC):
    """Interface for data mapping."""
    
    @abstractmethod
    def user_from_dict(self, data: Dict[str, Any]) -> "User":
        """Map dict to User."""
        pass
    
    @abstractmethod
    def message_from_dict(self, data: Dict[str, Any], chat_id: int, client: Optional[Any] = None) -> "Message":
        """Map dict to Message."""
        pass
    
    @abstractmethod
    def chat_from_dict(self, data: Dict[str, Any], client: Optional[Any] = None) -> "Chat":
        """Map dict to Chat."""
        pass