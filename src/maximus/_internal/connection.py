import asyncio
import json
from typing import Optional, Callable, Dict, Any, List, Protocol
from contextlib import asynccontextmanager

try:
    import websockets
    from websockets.exceptions import ConnectionClosed
except ImportError:
    websockets = None
    ConnectionClosed = Exception

from ..errors.connection import ConnectionError
from .interfaces import IConnection
from .constants import WEBSOCKET_URL, DEFAULT_CHATS_COUNT, Messages, call_handlers


class ConnectionAdapter(Protocol):
    """Protocol for connection adapters."""
    
    async def connect(self, url: str, headers: Dict[str, str]) -> None:
        ...
    
    async def send(self, data: str) -> None:
        ...
    
    async def receive(self) -> str:
        ...
    
    async def close(self) -> None:
        ...
    
    @property
    def is_connected(self) -> bool:
        ...


class WebSocketConnection:
    """WebSocket connection implementation."""
    
    def __init__(self) -> None:
        self._websocket: Optional[Any] = None
        self._is_connected = False
    
    async def connect(self, url: str, headers: Dict[str, str]) -> None:
        """Connect to WebSocket."""
        if websockets is None:
            raise ConnectionError("websockets library not installed")
        
        try:
            self._websocket = await websockets.connect(url, extra_headers=headers)
            self._is_connected = True
        except Exception as e:
            raise ConnectionError(f"Failed to connect: {e}")
    
    async def send(self, data: str) -> None:
        """Send data through WebSocket."""
        if not self._websocket or not self._is_connected:
            raise ConnectionError("Not connected")
        
        try:
            await self._websocket.send(data)
        except ConnectionClosed:
            self._is_connected = False
            raise ConnectionError("Connection closed")
    
    async def receive(self) -> str:
        """Receive data from WebSocket."""
        if not self._websocket or not self._is_connected:
            raise ConnectionError("Connection closed")
        
        try:
            return await self._websocket.recv()
        except ConnectionClosed:
            self._is_connected = False
            raise ConnectionError("Connection closed")
    
    async def close(self) -> None:
        """Close WebSocket connection."""
        if self._websocket:
            await self._websocket.close()
        self._is_connected = False
    
    @property
    def is_connected(self) -> bool:
        """Check if connected."""
        return self._is_connected


class MaxConnection(IConnection):
    """MAX API connection implementation."""
    
    def __init__(self, connection: ConnectionAdapter, session_data: Dict[str, Any], debug: bool = False) -> None:
        self._connection = connection
        self._session_data = session_data
        self._debug = debug
        self._seq = 0
        self._message_handlers: Dict[str, List[Callable]] = {}
    
    async def connect(self) -> None:
        """Connect to MAX API."""
        headers = self._get_headers()
        await self._connection.connect(WEBSOCKET_URL, headers)
        await self._initialize()
        asyncio.create_task(self._listen())
    
    async def disconnect(self) -> None:
        """Disconnect from MAX API."""
        await self._connection.close()
    
    def is_connected(self) -> bool:
        """Check if connected."""
        return self._connection.is_connected
    
    def register_event_handler(self, event: str, handler: Callable) -> None:
        """Register internal event handler."""
        if event not in self._message_handlers:
            self._message_handlers[event] = []
        self._message_handlers[event].append(handler)
    
    async def send_message(self, chat_id: int, text: str, reply_to: Optional[str] = None) -> int:
        """Send a message."""
        import time
        cid = int(time.time() * 1000)
        
        message_data = {
            "text": text,
            "cid": cid,
            "elements": [],
            "attaches": []
        }
        
        if reply_to:
            message_data["replyTo"] = reply_to
        
        payload = {
            "chatId": chat_id,
            "message": message_data,
            "notify": True
        }
        
        message = self._create_message(64, payload)
        await self._send(message)
        return self._seq
    
    async def send_sticker(self, chat_id: int, sticker_id: int, reply_to: Optional[str] = None) -> int:
        """Send a sticker."""
        import time
        cid = int(time.time() * 1000)
        
        message_data = {
            "cid": cid,
            "attaches": [{
                "_type": "STICKER",
                "stickerId": sticker_id
            }]
        }
        
        if reply_to:
            message_data["replyTo"] = reply_to
        
        payload = {
            "chatId": chat_id,
            "message": message_data,
            "notify": True
        }
        
        message = self._create_message(64, payload)
        await self._send(message)
        return self._seq
    
    async def send_reaction(self, chat_id: int, message_id: str, reaction_type: str = "EMOJI", reaction_id: str = "👍") -> int:
        """Send a reaction."""
        payload = {
            "chatId": chat_id,
            "messageId": message_id,
            "reaction": {
                "reactionType": reaction_type,
                "id": reaction_id
            }
        }
        
        message = self._create_message(178, payload)
        await self._send(message)
        return self._seq
    
    async def edit_message(self, chat_id: int, message_id: str, text: str) -> int:
        """Edit a message."""
        payload = {
            "chatId": chat_id,
            "messageId": message_id,
            "text": text
        }
        message = self._create_message(21, payload)
        await self._send(message)
        return self._seq
    
    async def delete_message(self, chat_id: int, message_id: str) -> int:
        """Delete a message."""
        payload = {
            "chatId": chat_id,
            "messageId": message_id
        }
        message = self._create_message(22, payload)
        await self._send(message)
        return self._seq
    
    async def send_events(self, events: List[Dict[str, Any]]) -> int:
        """Send events."""
        payload = {"events": events}
        message = self._create_message(5, payload)
        await self._send(message)
        return self._seq
    async def send_auth_start(self, phone: str, language: str = "ru") -> int:
        """Start authentication."""
        payload = {
            "phone": phone,
            "type": "START_AUTH",
            "language": language
        }
        message = self._create_message(17, payload)
        await self._send(message)
        return self._seq
    
    async def send_auth_code(self, token: str, verify_code: str) -> int:
        """Send auth code."""
        payload = {
            "token": token,
            "verifyCode": verify_code,
            "authTokenType": "CHECK_CODE"
        }
        message = self._create_message(18, payload)
        await self._send(message)
        return self._seq
    
    async def send_auth_token(self, token: str, interactive: bool = False, chats_count: int = DEFAULT_CHATS_COUNT) -> int:
        """Send auth token."""
        payload = {
            "interactive": interactive,
            "token": token,
            "chatsCount": chats_count,
            "chatsSync": 0,
            "contactsSync": 0,
            "presenceSync": 0,
            "draftsSync": 0
        }
        message = self._create_message(19, payload)
        await self._send(message)
        return self._seq
    
    async def send_get_chats(self, chat_ids: List[int]) -> int:
        """Get chats."""
        payload = {"chatIds": chat_ids}
        message = self._create_message(48, payload)
        await self._send(message)
        return self._seq
    
    async def send_get_contacts(self, contact_ids: List[int]) -> int:
        """Get contacts."""
        payload = {"contactIds": contact_ids}
        message = self._create_message(32, payload)
        await self._send(message)
        return self._seq
    
    def _get_headers(self) -> Dict[str, str]:
        """Get connection headers."""
        user_agent = self._session_data.get("user_agent", "")
        return {
            "Origin": "https://web.max.ru",
            "User-Agent": user_agent,
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }
    
    def _create_message(self, opcode: int, payload: Dict[str, Any], cmd: int = 0) -> Dict[str, Any]:
        """Create protocol message."""
        self._seq += 1
        return {
            "ver": self._session_data.get("version", 11),
            "cmd": cmd,
            "seq": self._seq,
            "opcode": opcode,
            "payload": payload
        }
    
    async def _send(self, message: Dict[str, Any]) -> None:
        """Send message through connection."""
        data = json.dumps(message)
        if self._debug:
            print(Messages.DEBUG_SENDING.format(json.dumps(message, indent=2, ensure_ascii=False)))
        await self._connection.send(data)
    
    async def _initialize(self) -> None:
        """Initialize connection."""
        print(Messages.DEVICE_INIT)
        init_payload = {
            "userAgent": self._get_user_agent_dict(),
            "deviceId": self._session_data.get("device_id", "")
        }
        message = self._create_message(6, init_payload)
        await self._send(message)
        device_id_short = self._session_data.get("device_id", "")[:8]
        print(Messages.DEVICE_INIT_SENT.format(device_id_short))
    
    def _get_user_agent_dict(self) -> Dict[str, Any]:
        """Get user agent dictionary."""
        return {
            "deviceType": self._session_data.get("device_type", "ANDROID"),
            "locale": self._session_data.get("locale", "ru"),
            "deviceLocale": self._session_data.get("device_locale", "ru"),
            "osVersion": self._session_data.get("os_version", "Windows"),
            "deviceName": self._session_data.get("device_name", "Chrome"),
            "headerUserAgent": self._session_data.get("user_agent", ""),
            "appVersion": self._session_data.get("app_version", "25.12.3"),
            "screen": self._session_data.get("screen", "1080x1920 1.0x"),
            "timezone": self._session_data.get("timezone", "Europe/Moscow")
        }
    
    async def _listen(self) -> None:
        """Listen for incoming messages."""
        while self.is_connected():
            try:
                data = await asyncio.wait_for(self._connection.receive(), timeout=1.0)
                if data:
                    try:
                        message = json.loads(data)
                        if self._debug:
                            print(Messages.DEBUG_RECEIVED.format(json.dumps(message, indent=2, ensure_ascii=False)))
                        await self._handle_message(message)
                    except json.JSONDecodeError:
                        if self._debug:
                            print(Messages.DEBUG_JSON_PARSE_FAILED.format(data))
                        continue
            except asyncio.TimeoutError:
                continue
            except ConnectionError:
                print(Messages.WEBSOCKET_CLOSED)
                break
            except Exception as err:
                print(Messages.ERROR_RECEIVING.format(err))
                continue
    
    async def _handle_message(self, message: Dict[str, Any]) -> None:
        """Handle incoming message."""
        if not message or not isinstance(message, dict):
            return
        
        opcode = message.get("opcode")
        cmd = message.get("cmd")
        payload = message.get("payload", {})
        
        event_name = None
        
        if cmd == 1:
            if opcode == 19:
                event_name = "auth_success"
            elif opcode == 17:
                event_name = "auth_code_requested"
            elif opcode == 18:
                event_name = "auth_code_checked"
            elif opcode == 64:
                event_name = "message_sent"
            elif opcode == 32:
                event_name = "contacts_update"
            elif opcode == 48:
                event_name = "chats_update"
        elif cmd == 3:
            if opcode == 19:
                event_name = "auth_error"
            elif opcode == 17:
                event_name = "auth_code_error"
        elif cmd == 0:
            if opcode == 128:
                event_name = "new_message"
        
        if event_name and event_name in self._message_handlers:
            await call_handlers(self._message_handlers[event_name], payload)