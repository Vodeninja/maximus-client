from typing import Optional, List, Dict, Any
from datetime import datetime

from sqlalchemy.orm import Session as SQLSession
from sqlalchemy.exc import SQLAlchemyError

from .database import DatabaseManager, Contact as ContactModel, SessionSetting
from .types import User


class ContactRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def save(self, user: User) -> bool:
        session = self.db_manager.get_session()
        try:
            contact = session.query(ContactModel).filter_by(id=user.id).first()
            
            if contact:
                contact.phone = user.phone
                contact.name = user.name
                contact.first_name = user.first_name
                contact.last_name = user.last_name
                contact.photo_id = user.photo_id
                contact.base_url = user.base_url
                contact.options = user.options or []
                contact.updated_at = datetime.utcnow()
            else:
                contact = ContactModel(
                    id=user.id,
                    phone=user.phone,
                    name=user.name,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    photo_id=user.photo_id,
                    base_url=user.base_url,
                    options=user.options or []
                )
                session.add(contact)
            
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Ошибка сохранения контакта: {e}")
            return False
        finally:
            session.close()
    
    def get(self, contact_id: int) -> Optional[User]:
        session = self.db_manager.get_session()
        try:
            contact = session.query(ContactModel).filter_by(id=contact_id).first()
            if not contact:
                return None
            
            return User(
                id=contact.id,
                phone=contact.phone,
                name=contact.name,
                first_name=contact.first_name,
                last_name=contact.last_name,
                photo_id=contact.photo_id,
                base_url=contact.base_url,
                options=contact.options or []
            )
        except SQLAlchemyError as e:
            print(f"Ошибка получения контакта: {e}")
            return None
        finally:
            session.close()
    
    def get_all(self) -> List[User]:
        session = self.db_manager.get_session()
        try:
            contacts = session.query(ContactModel).all()
            return [
                User(
                    id=contact.id,
                    phone=contact.phone,
                    name=contact.name,
                    first_name=contact.first_name,
                    last_name=contact.last_name,
                    photo_id=contact.photo_id,
                    base_url=contact.base_url,
                    options=contact.options or []
                )
                for contact in contacts
            ]
        except SQLAlchemyError as e:
            print(f"Ошибка получения контактов: {e}")
            return []
        finally:
            session.close()
    
    def save_batch(self, users: List[User]) -> int:
        session = self.db_manager.get_session()
        saved_count = 0
        try:
            for user in users:
                contact = session.query(ContactModel).filter_by(id=user.id).first()
                
                if contact:
                    contact.phone = user.phone
                    contact.name = user.name
                    contact.first_name = user.first_name
                    contact.last_name = user.last_name
                    contact.photo_id = user.photo_id
                    contact.base_url = user.base_url
                    contact.options = user.options or []
                    contact.updated_at = datetime.utcnow()
                else:
                    contact = ContactModel(
                        id=user.id,
                        phone=user.phone,
                        name=user.name,
                        first_name=user.first_name,
                        last_name=user.last_name,
                        photo_id=user.photo_id,
                        base_url=user.base_url,
                        options=user.options or []
                    )
                    session.add(contact)
                
                saved_count += 1
            
            session.commit()
            return saved_count
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Ошибка пакетного сохранения контактов: {e}")
            return saved_count
        finally:
            session.close()


class SessionRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def save_setting(self, key: str, value: str) -> bool:
        session = self.db_manager.get_session()
        try:
            setting = session.query(SessionSetting).filter_by(key=key).first()
            
            if setting:
                setting.value = value
            else:
                setting = SessionSetting(key=key, value=value)
                session.add(setting)
            
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Ошибка сохранения настройки: {e}")
            return False
        finally:
            session.close()
    
    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        session = self.db_manager.get_session()
        try:
            setting = session.query(SessionSetting).filter_by(key=key).first()
            return setting.value if setting else default
        except SQLAlchemyError as e:
            print(f"Ошибка получения настройки: {e}")
            return default
        finally:
            session.close()
    
    def save_settings(self, settings: Dict[str, str]) -> bool:
        session = self.db_manager.get_session()
        try:
            for key, value in settings.items():
                setting = session.query(SessionSetting).filter_by(key=key).first()
                
                if setting:
                    setting.value = value
                else:
                    setting = SessionSetting(key=key, value=value)
                    session.add(setting)
            
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Ошибка сохранения настроек: {e}")
            return False
        finally:
            session.close()
    
    def get_all_settings(self) -> Dict[str, str]:
        session = self.db_manager.get_session()
        try:
            settings = session.query(SessionSetting).all()
            return {setting.key: setting.value for setting in settings}
        except SQLAlchemyError as e:
            print(f"Ошибка получения настроек: {e}")
            return {}
        finally:
            session.close()
