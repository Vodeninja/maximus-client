import asyncio
from typing import Optional, Callable, List, Dict, Any
from .connection import MaximusConnection
from .session import Session
from .types import Chat, User, Message
from .utils import create_cold_start_event, create_go_event
from .storage import ContactRepository


class MaxClient:
    def __init__(
        self,
        session: Optional[str] = None,
        device_id: Optional[str] = None,
        user_agent: Optional[str] = None,
        app_version: Optional[str] = None,
        device_type: str = "WEB",
        locale: str = "ru",
        device_locale: str = "ru",
        os_version: str = "Windows",
        device_name: str = "Chrome",
        screen: str = "1080x1920 1.0x",
        timezone: str = "Europe/Moscow",
        version: int = 11,
        debug: bool = False
    ):
        if session is None:
            session = "session.maximus"
        
        self.session = Session(
            session_file=session,
            device_id=device_id,
            user_agent=user_agent,
            app_version=app_version,
            device_type=device_type,
            locale=locale,
            device_locale=device_locale,
            os_version=os_version,
            device_name=device_name,
            screen=screen,
            timezone=timezone,
            version=version
        )
        self.debug = debug
        self.connection = MaximusConnection(self.session, debug=debug)
        self.token: Optional[str] = self.session.token
        self.user: Optional[User] = None
        self.chats: Dict[int, Chat] = {}
        self.users: Dict[int, User] = {}
        self._code_callback: Optional[Callable] = None
        self._auth_future: Optional[asyncio.Future] = None
        self._event_handlers: Dict[str, List[Callable]] = {}
        self._phone: Optional[str] = self.session.phone
        self._code_callback_stored: Optional[Callable] = None
        
        db_manager = self.session.db_manager
        self._contact_repo = ContactRepository(db_manager) if db_manager else None
        
        self._setup_handlers()
    
    def _setup_handlers(self):
        self.connection.on_auth_success = self._on_auth_success
        self.connection.on_auth_code_requested = self._on_auth_code_requested
        self.connection.on_auth_code_checked = self._on_auth_code_checked
        self.connection.on_new_message = self._on_new_message
        self.connection.on_contacts_update = self._on_contacts_update
        self.connection.on_chats_update = self._on_chats_update
        self.connection.on_message_sent = self._on_message_sent
        self.connection.on_auth_error = self._on_auth_error
        self.connection.on_auth_code_error = self._on_auth_code_error
        self._phone: Optional[str] = None
        self._code_callback_stored: Optional[Callable] = None
    
    async def _on_auth_success(self, payload: Dict[str, Any]):

        new_token = payload.get("token")
        if new_token:
            self.token = new_token
            self.session.token = new_token
            self.session.save()

        
        profile = payload.get("profile", {})
        contact = profile.get("contact", {})
        if contact:
            self.user = User.from_dict({"contact": contact})
            user_name = self.user.name or f"User {self.user.id}"
            print(f"👤 Пользователь: {user_name} (ID: {self.user.id})")
        
        chats_data = payload.get("chats", [])
        print(f"💬 Загружено чатов: {len(chats_data)}")
        for chat_data in chats_data:
            chat = Chat.from_dict(chat_data, client=self)
            self.chats[chat.id] = chat
            
            if chat.type.value == "DIALOG" and not chat.title:
                participant_ids = list(chat.participants.keys())
                for pid in participant_ids:
                    user = self.get_user(pid)
                    if user and user.name:
                        chat.title = user.name
                        break
        
        if self._auth_future and not self._auth_future.done():
            self._auth_future.set_result(True)
        
        await self._sync_after_auth()
        await self._dispatch_event("ready")
    
    async def _sync_after_auth(self):
        try:
            if self._contact_repo:
                saved_contacts = self._contact_repo.get_all()
                for user in saved_contacts:
                    self.users[user.id] = user
                    
                    if user.id in self.chats:
                        chat = self.chats[user.id]
                        if not chat.title and user.name:
                            chat.title = user.name
            
            if 0 in self.chats:
                await self.connection.send_get_chats([0])
            
            contact_ids = set()
            if self.user:
                contact_ids.add(self.user.id)
            for chat in self.chats.values():
                contact_ids.update(chat.participants.keys())
            
            if contact_ids:
                await self.connection.send_get_contacts(list(contact_ids)[:50])
        except Exception as err:
            print(f"Error syncing: {err}")
    
    async def _on_auth_code_requested(self, payload: Dict[str, Any]):
        token = payload.get("token")
        print("Code verification requested")
        if self._code_callback:
            code = await self._code_callback()
            if code:
                print("Sending code verification...")
                await self.connection.send_auth_code(token, code)
                print("✅ Код отправлен")
    
    async def _on_auth_code_checked(self, payload: Dict[str, Any]):
        token_attrs = payload.get("tokenAttrs", {})
        login_token = token_attrs.get("LOGIN", {}).get("token")
        
        if login_token:
            print("Code verified, authorization token received")
            self.session.token = login_token
            self.session.save()
            print("Token saved to session")
            print("Sending token to complete authorization...")
            await self.connection.send_auth_token(login_token, interactive=False, chats_count=40)
            print("Token sent")
    
    async def _on_new_message(self, payload: Dict[str, Any]):
        chat_id = payload.get("chatId")
        message_data = payload.get("message", {})
        
        if message_data and chat_id:
            message = Message.from_dict(message_data, chat_id, client=self)
            await self._dispatch_event("new_message", message)
    
    async def _on_contacts_update(self, payload: Dict[str, Any]):
        contacts = payload.get("contacts", [])
        for contact_data in contacts:
            user = User.from_dict(contact_data)
            self.users[user.id] = user
            
            if self._contact_repo:
                self._contact_repo.save(user)
            
            if user.id in self.chats:
                chat = self.chats[user.id]
                if not chat.title and user.name:
                    chat.title = user.name
        
        await self._dispatch_event("contacts_update", [User.from_dict(c) for c in contacts])
    
    async def _on_chats_update(self, payload: Dict[str, Any]):
        chats_data = payload.get("chats", [])
        for chat_data in chats_data:
            chat = Chat.from_dict(chat_data, client=self)
            self.chats[chat.id] = chat
            
            if chat.type.value == "DIALOG" and not chat.title:
                participant_ids = list(chat.participants.keys())
                for pid in participant_ids:
                    user = self.get_user(pid)
                    if user and user.name:
                        chat.title = user.name
                        break
    
    async def _on_message_sent(self, payload: Dict[str, Any]):
        message_data = payload.get("message", {})
        chat_id = payload.get("chatId")
        
        if message_data and chat_id:
            message = Message.from_dict(message_data, chat_id, client=self)
            await self._dispatch_event("message_sent", message)
    
    async def _on_auth_error(self, payload: Dict[str, Any]):
        error = payload.get("error")
        message = payload.get("message")
        
        print(f"❌ Authorization error: {message}")
        
        if error == "login.token" or message == "FAIL_LOGIN_TOKEN":
            print("🔑 Token invalid, re-authorization required")
            self.token = None
            self.session.token = None
            self.session.save()
            
            if self._phone:
                print("📱 Requesting re-authorization by phone...")
                await self.connection.send_auth_start(self._phone, "ru")
                
                events = [
                    create_cold_start_event(),
                    create_go_event(1)
                ]
                await self.connection.send_events(events)
                
                if self._code_callback_stored:
                    self._code_callback = self._code_callback_stored
                
                self._auth_future = asyncio.Future()
                try:
                    await asyncio.wait_for(self._auth_future, timeout=60.0)
                    print("✅ Re-authorization successful")
                except asyncio.TimeoutError:
                    print("⚠️ Authorization timeout")
            else:
                print("⚠️ Phone number not found, manual authorization required")
                await self._dispatch_event("auth_required")
    
    async def _on_auth_code_error(self, payload: Dict[str, Any]):
        error = payload.get("error")
        message = payload.get("message")
        localized_message = payload.get("localizedMessage", message)
        
        print(f"❌ Authorization code error: {localized_message}")
        
        if error == "error.limit.violate":
            print("⚠️ Too many attempts, please try again later")
            await self._dispatch_event("auth_limit_exceeded", payload)
        else:
            await self._dispatch_event("auth_code_error", payload)
    
    async def start(
        self,
        phone: Optional[str] = None,
        code_callback: Optional[Callable] = None
    ):
        print("Connecting to WebSocket...")
        await self.connection.connect()
        print("Connected to WebSocket")
        
        if self.token:
            print("Found saved token, authorization...")
            await asyncio.sleep(0.5)
            await self.connection.send_auth_token(
                self.token,
                interactive=False,
                chats_count=40
            )
            print("Token sent")
            self._auth_future = asyncio.Future()
            await self._auth_future
            await self._sync_after_auth()
            return
        
        if phone:
            print(f"Sending phone number: {phone}")
            self._phone = phone
            self.session.phone = phone
            self.session.save()
            self._code_callback = code_callback
            self._code_callback_stored = code_callback
            await self.connection.send_auth_start(phone, "ru")
            print("Phone number sent")
            
            events = [
                create_cold_start_event(),
                create_go_event(1)
            ]
            await self.connection.send_events(events)
            print("Navigation events sent")
            
            self._auth_future = asyncio.Future()
            await self._auth_future
    
    async def connect(self):
        await self.start()
    
    async def disconnect(self):
        await self.connection.disconnect()
    
    def get_chats(self) -> List[Chat]:
        return list(self.chats.values())
    
    def get_chat(self, chat_id: int) -> Optional[Chat]:
        chat = self.chats.get(chat_id)
        if chat and not chat._client:
            chat._client = self
        return chat
    
    def get_user(self, user_id: int) -> Optional[User]:
        if user_id in self.users:
            return self.users[user_id]
        
        if self._contact_repo:
            user = self._contact_repo.get(user_id)
            if user:
                self.users[user_id] = user
                return user
        
        return None
    
    def get_entity(self, entity_id: int) -> Optional[Any]:
        entity = self.get_chat(entity_id)
        if entity:
            return entity
        return self.get_user(entity_id)
    
    def iter_chats(self):
        return iter(self.chats.values())
    
    def iter_users(self):
        return iter(self.users.values())
    
    async def send_message(self, chat_id: int, text: str, reply_to: Optional[str] = None) -> Optional[Message]:
        if not self.connection.is_connected:
            print("Connection lost, reconnecting before sending...")
            await self._reconnect()
        await self.connection.send_message(chat_id, text, reply_to)
        return None
    
    async def send_sticker(self, chat_id: int, sticker_id: int, reply_to: Optional[str] = None) -> Optional[Message]:
        """Send a sticker to a chat.
        
        Args:
            chat_id (int): Target chat ID
            sticker_id (int): Sticker ID to send
            reply_to (str, optional): ID of message to reply to
            
        Returns:
            Optional[Message]: Message object (may be None)
        """
        if not self.connection.is_connected:
            print("Connection lost, reconnecting before sending...")
            await self._reconnect()
        await self.connection.send_sticker(chat_id, sticker_id, reply_to)
        return None
    
    async def edit_message(self, chat_id: int, message_id: str, text: str) -> Optional[Message]:
        payload = {
            "chatId": chat_id,
            "messageId": message_id,
            "text": text
        }
        message = self.connection.create_message(21, payload)
        await self.connection.send(message)
        return None
    
    async def delete_message(self, chat_id: int, message_id: str):
        payload = {
            "chatId": chat_id,
            "messageId": message_id
        }
        message = self.connection.create_message(22, payload)
        await self.connection.send(message)
    
    async def run_until_disconnected(self):
        try:
            while True:
                if not self.connection.is_connected:
                    await self._reconnect()
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            await self.disconnect()
    
    async def _reconnect(self):
        try:
            await asyncio.sleep(2)
            print("Reconnecting to WebSocket...")
            await self.connection.connect()
            if self.token:
                await asyncio.sleep(0.5)
                print("🔑 Авторизация по токену...")
                await self.connection.send_auth_token(
                    self.token,
                    interactive=False,
                    chats_count=40
                )
                reconnect_future = asyncio.Future()
                self._auth_future = reconnect_future
                try:
                    await asyncio.wait_for(reconnect_future, timeout=10.0)
                    print("reconnect and authorization completed")
                except asyncio.TimeoutError:
                    print("Timeout waiting for authorization during reconnect")
            else:
                print("Token not found, re-authorization required")
        except Exception as e:
            print(f"Error reconnecting: {e}")
            await asyncio.sleep(5)
    
    def on(self, event_name: str):
        def decorator(func: Callable):
            if event_name not in self._event_handlers:
                self._event_handlers[event_name] = []
            self._event_handlers[event_name].append(func)
            return func
        return decorator
    
    async def _dispatch_event(self, event_name: str, *args, **kwargs):
        if event_name in self._event_handlers:
            for handler in self._event_handlers[event_name]:
                if asyncio.iscoroutinefunction(handler):
                    await handler(*args, **kwargs)
                else:
                    handler(*args, **kwargs)
    
    def add_event_handler(self, event_name: str, handler: Callable):
        if event_name not in self._event_handlers:
            self._event_handlers[event_name] = []
        self._event_handlers[event_name].append(handler)
    
    def remove_event_handler(self, event_name: str, handler: Callable):
        if event_name in self._event_handlers:
            if handler in self._event_handlers[event_name]:
                self._event_handlers[event_name].remove(handler)
