import asyncio
from typing import Optional, Callable, Union, Dict, Any
from ..errors import AuthError
from .interfaces import IConnection, ISessionManager
from .constants import DEFAULT_CHATS_COUNT, AUTH_DELAY, AUTH_TIMEOUT, Messages


class AuthManager:
    """Authentication manager."""
    
    def __init__(self, connection: IConnection, session: ISessionManager) -> None:
        self._connection = connection
        self._session = session
        self._auth_future: Optional[asyncio.Future] = None
        self._code_callback: Optional[Callable] = None
        self._phone: Optional[str] = None
        
        self._setup_handlers()
    
    def _setup_handlers(self) -> None:
        """Setup authentication event handlers."""
        self._connection.register_event_handler("auth_success", self._on_auth_success)
        self._connection.register_event_handler("auth_code_requested", self._on_auth_code_requested)
        self._connection.register_event_handler("auth_code_checked", self._on_auth_code_checked)
        self._connection.register_event_handler("auth_error", self._on_auth_error)
        self._connection.register_event_handler("auth_code_error", self._on_auth_code_error)
    
    async def authenticate(
        self,
        phone: Optional[str] = None,
        code_callback: Optional[Callable[[], Union[str, asyncio.Future[str]]]] = None
    ) -> None:
        """Authenticate user."""
        token = self._session.get("token")
        if token:
            print(Messages.FOUND_TOKEN)
            await asyncio.sleep(AUTH_DELAY)
            await self._connection.send_auth_token(token, interactive=False, chats_count=DEFAULT_CHATS_COUNT)
            print(Messages.TOKEN_SENT)
            self._auth_future = asyncio.Future()
            await self._auth_future
            return
        
        if phone:
            print(Messages.PHONE_SENDING.format(phone))
            self._phone = phone
            self._session.set("phone", phone)
            await self._session.save()
            self._code_callback = code_callback
            await self._connection.send_auth_start(phone, "ru")
            print(Messages.PHONE_SENT)
            
            # Send navigation events
            events = [
                {"type": "COLD_START", "time": int(asyncio.get_event_loop().time() * 1000)},
                {"type": "GO", "page": 1, "time": int(asyncio.get_event_loop().time() * 1000)}
            ]
            await self._connection.send_events(events)
            print(Messages.NAVIGATION_EVENTS_SENT)
            
            self._auth_future = asyncio.Future()
            await self._auth_future
    
    async def _on_auth_success(self, payload: Dict[str, Any]) -> None:
        """Handle auth success."""
        new_token = payload.get("token")
        if new_token:
            self._session.set("token", new_token)
            await self._session.save()
        
        if self._auth_future and not self._auth_future.done():
            self._auth_future.set_result(payload)
    
    async def _on_auth_code_requested(self, payload: Dict[str, Any]) -> None:
        """Handle auth code request."""
        token = payload.get("token")
        print(Messages.CODE_REQUESTED)
        if self._code_callback:
            code = self._code_callback()
            if asyncio.iscoroutine(code):
                code = await code
            if code:
                print(Messages.SENDING_CODE)
                await self._connection.send_auth_code(token, code)
                print(Messages.CODE_SENT)
    
    async def _on_auth_code_checked(self, payload: Dict[str, Any]) -> None:
        """Handle auth code check."""
        token_attrs = payload.get("tokenAttrs", {})
        login_token = token_attrs.get("LOGIN", {}).get("token")
        
        if login_token:
            print(Messages.CODE_VERIFIED)
            self._session.set("token", login_token)
            await self._session.save()
            print(Messages.TOKEN_SAVED)
            print(Messages.SENDING_TOKEN)
            await self._connection.send_auth_token(login_token, interactive=False, chats_count=DEFAULT_CHATS_COUNT)
            print(Messages.TOKEN_SENT)
    
    async def _on_auth_error(self, payload: Dict[str, Any]) -> None:
        """Handle auth error."""
        error = payload.get("error")
        message = payload.get("message")
        
        print(Messages.AUTH_ERROR.format(message))
        
        if error == "login.token" or message == "FAIL_LOGIN_TOKEN":
            print(Messages.TOKEN_INVALID)
            self._session.set("token", None)
            await self._session.save()
            
            if self._phone:
                print(Messages.REQUESTING_REAUTH)
                await self._connection.send_auth_start(self._phone, "ru")
                
                events = [
                    {"type": "COLD_START", "time": int(asyncio.get_event_loop().time() * 1000)},
                    {"type": "GO", "page": 1, "time": int(asyncio.get_event_loop().time() * 1000)}
                ]
                await self._connection.send_events(events)
                
                self._auth_future = asyncio.Future()
                try:
                    await asyncio.wait_for(self._auth_future, timeout=AUTH_TIMEOUT)
                    print(Messages.REAUTH_SUCCESSFUL)
                except asyncio.TimeoutError:
                    print(Messages.AUTH_TIMEOUT)
            else:
                print(Messages.PHONE_NOT_FOUND)
                if self._auth_future and not self._auth_future.done():
                    self._auth_future.set_exception(AuthError("Phone number not found"))
        else:
            if self._auth_future and not self._auth_future.done():
                self._auth_future.set_exception(AuthError(f"Auth error: {message}"))
    
    async def _on_auth_code_error(self, payload: Dict[str, Any]) -> None:
        """Handle auth code error."""
        error = payload.get("error")
        message = payload.get("message")
        localized_message = payload.get("localizedMessage", message)
        
        print(Messages.AUTH_CODE_ERROR.format(localized_message))
        
        if error == "error.limit.violate":
            print(Messages.TOO_MANY_ATTEMPTS)
        
        if self._auth_future and not self._auth_future.done():
            self._auth_future.set_exception(AuthError(f"Auth code error: {localized_message}"))