import asyncio
import json
import websockets
from typing import Optional, Callable, Dict, Any, List
from .session import Session


class MaximusConnection:
    def __init__(self, session: Session, debug: bool = False):
        self.session = session
        self.debug = debug
        self.ws_url = "wss://ws-api.oneme.ru/websocket"
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.seq: int = 0
        self.is_connected: bool = False
        self.message_handlers: Dict[int, Callable] = {}
        self.event_handlers: Dict[str, Callable] = {}
        
    def get_headers(self) -> Dict[str, str]:
        return self.session.get_headers()
    
    def create_message(self, opcode: int, payload: Dict[str, Any], cmd: int = 0) -> Dict[str, Any]:
        self.seq += 1
        return {
            "ver": self.session.version,
            "cmd": cmd,
            "seq": self.seq,
            "opcode": opcode,
            "payload": payload
        }
    
    async def send_message(self, chat_id: int, text: str, reply_to: Optional[str] = None):
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
        
        message = self.create_message(64, payload)
        await self.send(message)
        return self.seq
    
    async def send_sticker(self, chat_id: int, sticker_id: int, reply_to: Optional[str] = None):
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
        
        message = self.create_message(64, payload)
        await self.send(message)
        return self.seq
    
    async def send_reaction(self, chat_id: int, message_id: str, reaction_type: str = "EMOJI", reaction_id: str = "👍"):
        """Send a reaction to a message.
        
        Args:
            chat_id (int): Chat ID where the message is
            message_id (str): ID of the message to react to
            reaction_type (str): Type of reaction (default: "EMOJI")
            reaction_id (str): Reaction emoji or ID (default: "👍")
        """
        payload = {
            "chatId": chat_id,
            "messageId": message_id,
            "reaction": {
                "reactionType": reaction_type,
                "id": reaction_id
            }
        }
        
        message = self.create_message(178, payload)
        await self.send(message)
        return self.seq
    
    async def connect(self):
        headers = self.get_headers()
        self.websocket = await websockets.connect(self.ws_url, extra_headers=headers)
        self.is_connected = True
        await self._initialize()
        asyncio.create_task(self._listen())
    
    async def _initialize(self):
        print("🔧 Инициализация устройства...")
        init_payload = {
            "userAgent": self.session.get_user_agent_dict(),
            "deviceId": self.session.device_id
        }
        message = self.create_message(6, init_payload)
        await self.send(message)
        print(f"📤 Отправлена инициализация (Device ID: {self.session.device_id[:8]}...)")
    
    async def send(self, message: Dict[str, Any]):
        if not self.websocket or not self.is_connected:
            raise RuntimeError("Not connected")
        try:
            if self.debug:
                print(f"[DEBUG] Sending: {json.dumps(message, indent=2, ensure_ascii=False)}")
            await self.websocket.send(json.dumps(message))
        except websockets.exceptions.ConnectionClosed:
            self.is_connected = False
            raise RuntimeError("Connection closed")
    
    async def send_events(self, events: List[Dict[str, Any]]):
        payload = {"events": events}
        message = self.create_message(5, payload)
        await self.send(message)
    
    async def send_auth_start(self, phone: str, language: str = "ru"):
        payload = {
            "phone": phone,
            "type": "START_AUTH",
            "language": language
        }
        message = self.create_message(17, payload)
        await self.send(message)
        return self.seq
    
    async def send_auth_code(self, token: str, verify_code: str):
        payload = {
            "token": token,
            "verifyCode": verify_code,
            "authTokenType": "CHECK_CODE"
        }
        message = self.create_message(18, payload)
        await self.send(message)
        return self.seq
    
    async def send_auth_token(self, token: str, interactive: bool = False, chats_count: int = 40):
        payload = {
            "interactive": interactive,
            "token": token,
            "chatsCount": chats_count,
            "chatsSync": 0,
            "contactsSync": 0,
            "presenceSync": 0,
            "draftsSync": 0
        }
        message = self.create_message(19, payload)
        await self.send(message)
        return self.seq
    
    async def send_get_chats(self, chat_ids: List[int]):
        payload = {"chatIds": chat_ids}
        message = self.create_message(48, payload)
        await self.send(message)
        return self.seq
    
    async def send_get_contacts(self, contact_ids: List[int]):
        payload = {"contactIds": contact_ids}
        message = self.create_message(32, payload)
        await self.send(message)
        return self.seq
    
    async def _listen(self):
        try:
            while self.is_connected:
                try:
                    data = await asyncio.wait_for(self.websocket.recv(), timeout=1.0)
                    if data:
                        try:
                            message = json.loads(data)
                            if message:
                                if self.debug:
                                    print(f"[DEBUG] Received: {json.dumps(message, indent=2, ensure_ascii=False)}")
                                await self._handle_message(message)
                        except json.JSONDecodeError:
                            if self.debug:
                                print(f"[DEBUG] Failed to parse JSON: {data}")
                            continue
                except asyncio.TimeoutError:
                    continue
                except websockets.exceptions.ConnectionClosed:
                    print("⚠️ WebSocket соединение закрыто")
                    self.is_connected = False
                    break
                except Exception as err:
                    print(f"⚠️ Ошибка при получении сообщения: {err}")
                    continue
        except Exception as err:
            print(f"❌ Критическая ошибка в _listen: {err}")
            self.is_connected = False
            if hasattr(self, 'on_error'):
                await self.on_error(err)
    
    async def _handle_message(self, message: Dict[str, Any]):
        if not message or not isinstance(message, dict):
            return
        
        opcode = message.get("opcode")
        cmd = message.get("cmd")
        payload = message.get("payload", {})
        
        if cmd == 1:
            if opcode == 19:
                if hasattr(self, 'on_auth_success'):
                    await self.on_auth_success(payload)
            elif opcode == 17:
                if hasattr(self, 'on_auth_code_requested'):
                    await self.on_auth_code_requested(payload)
            elif opcode == 18:
                if hasattr(self, 'on_auth_code_checked'):
                    await self.on_auth_code_checked(payload)
            elif opcode == 64:
                if hasattr(self, 'on_message_sent'):
                    await self.on_message_sent(payload)
            elif opcode == 32:
                if hasattr(self, 'on_contacts_update'):
                    await self.on_contacts_update(payload)
        elif cmd == 3:
            if opcode == 19:
                if hasattr(self, 'on_auth_error'):
                    await self.on_auth_error(payload)
            elif opcode == 17:
                if hasattr(self, 'on_auth_code_error'):
                    await self.on_auth_code_error(payload)
        elif cmd == 0:
            if opcode == 128:
                if hasattr(self, 'on_new_message'):
                    await self.on_new_message(payload)
        
        if opcode in self.message_handlers:
            handler = self.message_handlers[opcode]
            if asyncio.iscoroutinefunction(handler):
                await handler(payload)
            else:
                handler(payload)
    
    def register_handler(self, opcode: int, handler: Callable):
        self.message_handlers[opcode] = handler
    
    async def disconnect(self):
        self.is_connected = False
        if self.websocket:
            await self.websocket.close()

