import asyncio
from typing import Optional, Callable, Dict, Any, List

from .types import Chat, User, Message
from ._internal.connection import MaxConnection, WebSocketConnection
from ._internal.session import SessionManager
from ._internal.mappers import DataMapper
from ._internal.event_dispatcher import EventDispatcher
from ._internal.auth_manager import AuthManager
from ._internal.data_manager import DataManager
from ._internal.constants import (
    DEFAULT_DEVICE_TYPE, DEFAULT_LOCALE, DEFAULT_OS_VERSION,
    DEFAULT_DEVICE_NAME, DEFAULT_SCREEN, DEFAULT_TIMEZONE, DEFAULT_VERSION,
    RECONNECT_DELAY, AUTH_DELAY, SYNC_DELAY, DEFAULT_CHATS_COUNT, Messages
)


class MaxClient:
    """MAX messenger client with clean OOP architecture."""
    
    def __init__(
        self,
        session: Optional[str] = None,
        device_id: Optional[str] = None,
        user_agent: Optional[str] = None,
        app_version: Optional[str] = None,
        device_type: str = DEFAULT_DEVICE_TYPE,
        locale: str = DEFAULT_LOCALE,
        device_locale: str = DEFAULT_LOCALE,
        os_version: str = DEFAULT_OS_VERSION,
        device_name: str = DEFAULT_DEVICE_NAME,
        screen: str = DEFAULT_SCREEN,
        timezone: str = DEFAULT_TIMEZONE,
        version: int = DEFAULT_VERSION,
        debug: bool = False
    ) -> None:
        # Initialize components
        self._session = SessionManager(session or "session.maximus")
        self._event_dispatcher = EventDispatcher()
        self._mapper = DataMapper()
        self._data_manager = DataManager(self._mapper)
        
        # Connection will be initialized in start()
        self._connection: Optional[MaxConnection] = None
        self._auth_manager: Optional[AuthManager] = None
        
        self._debug = debug
        
        # Configure session
        self._configure_session(
            device_id, user_agent, app_version, device_type,
            locale, device_locale, os_version, device_name,
            screen, timezone, version
        )
    
    def _configure_session(
        self,
        device_id: Optional[str],
        user_agent: Optional[str],
        app_version: Optional[str],
        device_type: str,
        locale: str,
        device_locale: str,
        os_version: str,
        device_name: str,
        screen: str,
        timezone: str,
        version: int
    ) -> None:
        """Configure session parameters."""
        if device_id:
            self._session.set("device_id", device_id)
        if user_agent:
            self._session.set("user_agent", user_agent)
        if app_version:
            self._session.set("app_version", app_version)
        
        self._session.set("device_type", device_type)
        self._session.set("locale", locale)
        self._session.set("device_locale", device_locale)
        self._session.set("os_version", os_version)
        self._session.set("device_name", device_name)
        self._session.set("screen", screen)
        self._session.set("timezone", timezone)
        self._session.set("version", version)
    
    def _setup_event_handlers(self) -> None:
        """Setup internal event handlers."""
        if not self._connection:
            return
        
        self._connection.register_event_handler("auth_success", self._on_auth_success)
        self._connection.register_event_handler("new_message", self._on_new_message)
        self._connection.register_event_handler("contacts_update", self._on_contacts_update)
        self._connection.register_event_handler("chats_update", self._on_chats_update)
        self._connection.register_event_handler("message_sent", self._on_message_sent)
    
    async def start(
        self,
        phone: Optional[str] = None,
        code_callback: Optional[Callable] = None
    ) -> None:
        """Start client and authenticate."""
        await self._session.load()
        
        # Initialize connection and auth manager
        session_data = self._session.get_all()
        self._connection = MaxConnection(WebSocketConnection(), session_data, debug=self._debug)
        self._auth_manager = AuthManager(self._connection, self._session)
        
        self._setup_event_handlers()
        
        print(Messages.CONNECTING_WEBSOCKET)
        await self._connection.connect()
        print(Messages.CONNECTED_WEBSOCKET)
        
        # Authenticate
        await self._auth_manager.authenticate(phone, code_callback)
        await self._sync_after_auth()
    
    async def connect(self) -> None:
        """Alias for start()."""
        await self.start()
    
    async def disconnect(self) -> None:
        """Disconnect from API."""
        if self._connection:
            await self._connection.disconnect()
    
    # Event system - direct delegation to EventDispatcher
    def on(self, event_type: str) -> Callable:
        """Decorator for event handlers."""
        return self._event_dispatcher.on(event_type)
    
    def add_event_handler(self, event_name: str, handler: Callable) -> None:
        """Add event handler."""
        self._event_dispatcher.add_event_handler(event_name, handler)
    
    def remove_event_handler(self, event_name: str, handler: Callable) -> None:
        """Remove event handler."""
        self._event_dispatcher.remove_event_handler(event_name, handler)
    
    # API methods with connection check
    async def _ensure_connected(self) -> None:
        """Ensure connection is active."""
        if not self._connection or not self._connection.is_connected():
            print(Messages.CONNECTION_LOST)
            await self._reconnect()
    
    async def send_message(self, chat_id: int, text: str, reply_to: Optional[str] = None) -> Optional[Message]:
        """Send a message."""
        await self._ensure_connected()
        await self._connection.send_message(chat_id, text, reply_to)
        return None
    
    async def send_sticker(self, chat_id: int, sticker_id: int, reply_to: Optional[str] = None) -> Optional[Message]:
        """Send a sticker."""
        await self._ensure_connected()
        await self._connection.send_sticker(chat_id, sticker_id, reply_to)
        return None
    
    async def send_reaction(self, chat_id: int, message_id: str, reaction: str = "👍") -> None:
        """Send a reaction."""
        await self._ensure_connected()
        await self._connection.send_reaction(chat_id, message_id, "EMOJI", reaction)
    
    async def edit_message(self, chat_id: int, message_id: str, text: str) -> Optional[Message]:
        """Edit a message."""
        if not self._connection:
            return None
        await self._connection.edit_message(chat_id, message_id, text)
        return None
    
    async def delete_message(self, chat_id: int, message_id: str) -> None:
        """Delete a message."""
        if not self._connection:
            return
        await self._connection.delete_message(chat_id, message_id)
    
    # Data access delegation
    def get_chats(self) -> List[Chat]:
        """Get list of chats."""
        return self._data_manager.get_chats()
    
    def get_chat(self, chat_id: int) -> Optional[Chat]:
        """Get specific chat."""
        chat = self._data_manager.get_chat(chat_id)
        if chat and not hasattr(chat, '_client'):
            object.__setattr__(chat, '_client', self)
        return chat
    
    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self._data_manager.get_user(user_id)
    
    def get_entity(self, entity_id: int) -> Optional[Chat | User]:
        """Get chat or user by ID."""
        return self.get_chat(entity_id) or self.get_user(entity_id)
    
    def iter_chats(self):
        """Iterate over chats."""
        return self._data_manager.iter_chats()
    
    def iter_users(self):
        """Iterate over users."""
        return self._data_manager.iter_users()
    
    @property
    def user(self) -> Optional[User]:
        """Current user."""
        return self._data_manager.user
    
    @property
    def chats(self) -> Dict[int, Chat]:
        """All chats."""
        return self._data_manager.chats
    
    async def run_until_disconnected(self) -> None:
        """Keep running until interrupted."""
        try:
            while True:
                if not self._connection or not self._connection.is_connected():
                    await self._reconnect()
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            await self.disconnect()
    
    async def _reconnect(self) -> None:
        """Reconnect to the service."""
        try:
            await asyncio.sleep(RECONNECT_DELAY)
            print(Messages.RECONNECTING_WEBSOCKET)
            if self._connection:
                await self._connection.connect()
            token = self._session.get("token")
            if token and self._connection:
                await asyncio.sleep(AUTH_DELAY)
                print(Messages.AUTH_BY_TOKEN)
                await self._connection.send_auth_token(token, interactive=False, chats_count=DEFAULT_CHATS_COUNT)
                print(Messages.RECONNECT_COMPLETED)
            else:
                print(Messages.TOKEN_NOT_FOUND)
        except Exception as e:
            print(Messages.ERROR_RECONNECTING.format(e))
            await asyncio.sleep(SYNC_DELAY)
    
    async def _sync_after_auth(self) -> None:
        """Sync data after authentication."""
        try:
            if 0 in self._data_manager.chats and self._connection:
                await self._connection.send_get_chats([0])
            
            contact_ids = set()
            if self._data_manager.user:
                contact_ids.add(self._data_manager.user.id)
            for chat in self._data_manager.chats.values():
                contact_ids.update(chat.participants.keys())
            
            if contact_ids and self._connection:
                await self._connection.send_get_contacts(list(contact_ids)[:50])
        except Exception as err:
            print(Messages.ERROR_SYNCING.format(err))
    
    # Event handlers
    async def _on_auth_success(self, payload: Dict[str, Any]) -> None:
        """Handle auth success."""
        profile = payload.get("profile", {})
        contact = profile.get("contact", {})
        if contact:
            self._data_manager.set_current_user({"contact": contact})
            user_name = self._data_manager.user.name or f"User {self._data_manager.user.id}"
            print(Messages.USER_INFO.format(user_name, self._data_manager.user.id))
        
        chats_data = payload.get("chats", [])
        print(Messages.CHATS_LOADED.format(len(chats_data)))
        self._data_manager.update_chats(chats_data, client=self)
        
        await self._event_dispatcher.dispatch_event("ready")
    
    async def _on_new_message(self, payload: Dict[str, Any]) -> None:
        """Handle new message."""
        chat_id = payload.get("chatId")
        message_data = payload.get("message", {})
        
        if message_data and chat_id:
            message = self._data_manager.create_message(message_data, chat_id, client=self)
            await self._event_dispatcher.dispatch_event("new_message", message)
    
    async def _on_contacts_update(self, payload: Dict[str, Any]) -> None:
        """Handle contacts update."""
        contacts = payload.get("contacts", [])
        users = self._data_manager.update_users(contacts)
        await self._event_dispatcher.dispatch_event("contacts_update", users)
    
    async def _on_chats_update(self, payload: Dict[str, Any]) -> None:
        """Handle chats update."""
        chats_data = payload.get("chats", [])
        self._data_manager.update_chats(chats_data, client=self)
    
    async def _on_message_sent(self, payload: Dict[str, Any]) -> None:
        """Handle message sent."""
        message_data = payload.get("message", {})
        chat_id = payload.get("chatId")
        
        if message_data and chat_id:
            message = self._data_manager.create_message(message_data, chat_id, client=self)
            await self._event_dispatcher.dispatch_event("message_sent", message)