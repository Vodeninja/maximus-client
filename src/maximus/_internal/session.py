import json
import os
from typing import Dict, Any, Optional
from uuid import uuid4
from .interfaces import ISessionManager
from .constants import (
    DEFAULT_USER_AGENT, DEFAULT_APP_VERSION, DEFAULT_DEVICE_TYPE,
    DEFAULT_LOCALE, DEFAULT_OS_VERSION, DEFAULT_DEVICE_NAME,
    DEFAULT_SCREEN, DEFAULT_TIMEZONE, DEFAULT_VERSION, Messages
)


class SessionManager(ISessionManager):
    """Session manager implementation."""
    
    def __init__(self, session_file: Optional[str] = None) -> None:
        self._session_file = session_file or "session.maximus"
        self._data: Dict[str, Any] = self._get_defaults()
    
    def _get_defaults(self) -> Dict[str, Any]:
        """Get default session values."""
        return {
            "device_id": str(uuid4()),
            "user_agent": DEFAULT_USER_AGENT,
            "app_version": DEFAULT_APP_VERSION,
            "device_type": DEFAULT_DEVICE_TYPE,
            "locale": DEFAULT_LOCALE,
            "device_locale": DEFAULT_LOCALE,
            "os_version": DEFAULT_OS_VERSION,
            "device_name": DEFAULT_DEVICE_NAME,
            "screen": DEFAULT_SCREEN,
            "timezone": DEFAULT_TIMEZONE,
            "version": DEFAULT_VERSION,
            "token": None,
            "phone": None
        }
    
    async def load(self) -> None:
        """Load session data from file."""
        if not os.path.exists(self._session_file):
            return
        
        try:
            with open(self._session_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for key, value in data.items():
                    self._data[key] = value
        except (json.JSONDecodeError, FileNotFoundError, PermissionError):
            pass
    
    async def save(self) -> None:
        """Save session data to file."""
        try:
            # Create directory if it doesn't exist
            dir_path = os.path.dirname(self._session_file)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            
            with open(self._session_file, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
        except (PermissionError, OSError) as e:
            print(Messages.ERROR_SAVING_SESSION.format(e))
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get session value."""
        return self._data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set session value."""
        self._data[key] = value
    
    def get_all(self) -> Dict[str, Any]:
        """Get all session data."""
        return self._data.copy()