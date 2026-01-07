import os
from typing import Optional, Dict, Any
from uuid import uuid4

from .database import DatabaseManager
from .storage import SessionRepository


class Session:
    def __init__(
        self,
        session_file: Optional[str] = None,
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
        version: int = 11
    ):
        self.session_file = session_file or "session.maximus"
        self.device_id = device_id or str(uuid4())
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/142.0.0.0 Safari/537.36"
        )
        self.app_version = app_version or "25.12.3"
        self.device_type = device_type
        self.locale = locale
        self.device_locale = device_locale
        self.os_version = os_version
        self.device_name = device_name
        self.screen = screen
        self.timezone = timezone
        self.version = version
        self.token: Optional[str] = None
        self.phone: Optional[str] = None
        
        self._db_manager: Optional[DatabaseManager] = None
        self._session_repo: Optional[SessionRepository] = None
        
        if self.session_file:
            self._init_storage()
            self.load()
    
    def _get_db_path(self) -> str:
        if not self.session_file:
            return None
        
        if self.session_file.endswith('.maximus'):
            return self.session_file
        
        return f"{self.session_file}.db"
    
    def _init_storage(self):
        db_path = self._get_db_path()
        if not db_path:
            return
        
        try:
            json_data = None
            if os.path.exists(self.session_file):
                temp_manager = DatabaseManager(db_path)
                json_data = temp_manager.migrate_from_json(self.session_file)
            
            self._db_manager = DatabaseManager(db_path)
            self._session_repo = SessionRepository(self._db_manager)
            
            if json_data:
                self._migrate_from_json(json_data)
                try:
                    if os.path.exists(self.session_file) and not self._db_manager.is_sqlite_file(self.session_file):
                        os.remove(self.session_file)
                except (OSError, PermissionError):
                    pass
        except Exception as e:
            print(f"Error initializing storage: {e}")
    
    def _migrate_from_json(self, data: Dict[str, Any]):
        self.device_id = data.get("device_id", self.device_id)
        self.user_agent = data.get("user_agent", self.user_agent)
        self.app_version = data.get("app_version", self.app_version)
        self.device_type = data.get("device_type", self.device_type)
        self.locale = data.get("locale", self.locale)
        self.device_locale = data.get("device_locale", self.device_locale)
        self.os_version = data.get("os_version", self.os_version)
        self.device_name = data.get("device_name", self.device_name)
        self.screen = data.get("screen", self.screen)
        self.timezone = data.get("timezone", self.timezone)
        self.version = data.get("version", self.version)
        self.token = data.get("token")
        self.phone = data.get("phone")
        self.save()
    
    def save(self):
        if not self._session_repo:
            return
        
        settings = {
            "device_id": self.device_id,
            "user_agent": self.user_agent,
            "app_version": self.app_version,
            "device_type": self.device_type,
            "locale": self.locale,
            "device_locale": self.device_locale,
            "os_version": self.os_version,
            "device_name": self.device_name,
            "screen": self.screen,
            "timezone": self.timezone,
            "version": str(self.version),
            "token": self.token or "",
            "phone": self.phone or ""
        }
        
        self._session_repo.save_settings(settings)
    
    def load(self):
        if not self._session_repo:
            return
        
        settings = self._session_repo.get_all_settings()
        
        if not settings:
            return
        
        self.device_id = settings.get("device_id", self.device_id)
        self.user_agent = settings.get("user_agent", self.user_agent)
        self.app_version = settings.get("app_version", self.app_version)
        self.device_type = settings.get("device_type", self.device_type)
        self.locale = settings.get("locale", self.locale)
        self.device_locale = settings.get("device_locale", self.device_locale)
        self.os_version = settings.get("os_version", self.os_version)
        self.device_name = settings.get("device_name", self.device_name)
        self.screen = settings.get("screen", self.screen)
        self.timezone = settings.get("timezone", self.timezone)
        self.version = int(settings.get("version", self.version))
        self.token = settings.get("token") or None
        self.phone = settings.get("phone") or None
    
    @property
    def db_manager(self) -> Optional[DatabaseManager]:
        return self._db_manager
    
    def get_user_agent_dict(self) -> Dict[str, Any]:
        return {
            "deviceType": self.device_type,
            "locale": self.locale,
            "deviceLocale": self.device_locale,
            "osVersion": self.os_version,
            "deviceName": self.device_name,
            "headerUserAgent": self.user_agent,
            "appVersion": self.app_version,
            "screen": self.screen,
            "timezone": self.timezone
        }
    
    def get_headers(self) -> Dict[str, str]:
        return {
            "Origin": "https://web.max.ru",
            "User-Agent": self.user_agent,
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6,zh-CN;q=0.5,zh;q=0.4",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }
