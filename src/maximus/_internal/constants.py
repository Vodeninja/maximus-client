"""Constants for the maximus library."""
import asyncio
from typing import Callable, Any, List

# Connection constants
WEBSOCKET_URL = "wss://ws-api.oneme.ru/websocket"
DEFAULT_CHATS_COUNT = 40
RECONNECT_DELAY = 2
AUTH_DELAY = 0.5
SYNC_DELAY = 5
AUTH_TIMEOUT = 60.0

# Default session values
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/142.0.0.0 Safari/537.36"
)
DEFAULT_APP_VERSION = "25.12.3"
DEFAULT_DEVICE_TYPE = "ANDROID"
DEFAULT_LOCALE = "ru"
DEFAULT_OS_VERSION = "Windows"
DEFAULT_DEVICE_NAME = "Chrome"
DEFAULT_SCREEN = "1080x1920 1.0x"
DEFAULT_TIMEZONE = "Europe/Moscow"
DEFAULT_VERSION = 11

# Messages
class Messages:
    # Connection messages
    CONNECTING_WEBSOCKET = "Connecting to WebSocket..."
    CONNECTED_WEBSOCKET = "Connected to WebSocket"
    RECONNECTING_WEBSOCKET = "Reconnecting to WebSocket..."
    CONNECTION_LOST = "Connection lost, reconnecting..."
    WEBSOCKET_CLOSED = "⚠️ WebSocket соединение закрыто"
    
    # Auth messages
    FOUND_TOKEN = "Found saved token, authorization..."
    TOKEN_SENT = "Token sent"
    PHONE_SENT = "Phone number sent"
    NAVIGATION_EVENTS_SENT = "Navigation events sent"
    CODE_REQUESTED = "Code verification requested"
    SENDING_CODE = "Sending code verification..."
    CODE_SENT = "✅ Код отправлен"
    CODE_VERIFIED = "Code verified, authorization token received"
    TOKEN_SAVED = "Token saved to session"
    SENDING_TOKEN = "Sending token to complete authorization..."
    AUTH_BY_TOKEN = "🔑 Авторизация по токену..."
    RECONNECT_COMPLETED = "reconnect and authorization completed"
    TOKEN_NOT_FOUND = "Token not found, re-authorization required"
    TOKEN_INVALID = "🔑 Token invalid, re-authorization required"
    REQUESTING_REAUTH = "📱 Requesting re-authorization by phone..."
    REAUTH_SUCCESSFUL = "✅ Re-authorization successful"
    AUTH_TIMEOUT = "⚠️ Authorization timeout"
    PHONE_NOT_FOUND = "⚠️ Phone number not found, manual authorization required"
    TOO_MANY_ATTEMPTS = "⚠️ Too many attempts, please try again later"
    
    # Device messages
    DEVICE_INIT = "🔧 Инициализация устройства..."
    
    # Error messages
    ERROR_RECEIVING = "⚠️ Ошибка при получении сообщения: {}"
    ERROR_RECONNECTING = "Error reconnecting: {}"
    ERROR_SYNCING = "Error syncing: {}"
    ERROR_SAVING_SESSION = "Error saving session: {}"
    AUTH_ERROR = "❌ Authorization error: {}"
    AUTH_CODE_ERROR = "❌ Authorization code error: {}"
    
    # Debug messages
    DEBUG_SENDING = "[DEBUG] Sending: {}"
    DEBUG_RECEIVED = "[DEBUG] Received: {}"
    DEBUG_JSON_PARSE_FAILED = "[DEBUG] Failed to parse JSON: {}"
    
    # Other messages
    DEVICE_INIT_SENT = "📤 Отправлена инициализация (Device ID: {}...)"
    PHONE_SENDING = "Sending phone number: {}"
    USER_INFO = "👤 Пользователь: {} (ID: {})"
    CHATS_LOADED = "💬 Загружено чатов: {}"


async def call_handlers(handlers: List[Callable], *args, **kwargs) -> None:
    """Utility function to call handlers (sync or async)."""
    for handler in handlers:
        if asyncio.iscoroutinefunction(handler):
            await handler(*args, **kwargs)
        else:
            handler(*args, **kwargs)