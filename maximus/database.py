import os
import json
import sqlite3
from typing import Optional
from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session as SQLSession
from sqlalchemy.engine import Engine

Base = declarative_base()


class SessionSetting(Base):
    __tablename__ = "session_settings"
    
    key = Column(String, primary_key=True)
    value = Column(Text, nullable=True)


class Contact(Base):
    __tablename__ = "contacts"
    
    id = Column(Integer, primary_key=True)
    phone = Column(Integer, nullable=True)
    name = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    photo_id = Column(Integer, nullable=True)
    base_url = Column(String, nullable=True)
    options = Column(JSON, nullable=True, default=list)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.engine: Optional[Engine] = None
        self.SessionLocal: Optional[sessionmaker] = None
        self._init_database()
    
    def _init_database(self):
        if not self.db_path:
            return
        
        try:
            dir_path = os.path.dirname(self.db_path) if os.path.dirname(self.db_path) else "."
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            
            db_url = f"sqlite:///{self.db_path}"
            self.engine = create_engine(
                db_url,
                connect_args={"check_same_thread": False},
                echo=False
            )
            
            Base.metadata.create_all(self.engine)
            
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
        except Exception as e:
            raise RuntimeError(f"Error initializing DB: {e}")
    
    def get_session(self) -> SQLSession:
        if not self.SessionLocal:
            raise RuntimeError("DB not initialized")
        return self.SessionLocal()
    
    def is_sqlite_file(self, file_path: str) -> bool:
        if not os.path.exists(file_path):
            return False
        
        try:
            conn = sqlite3.connect(file_path)
            conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            conn.close()
            return True
        except (sqlite3.DatabaseError, sqlite3.OperationalError):
            return False
    
    def migrate_from_json(self, json_path: str) -> Optional[dict]:
        if not os.path.exists(json_path):
            return None
        
        if self.is_sqlite_file(json_path):
            return None
        
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
        except (json.JSONDecodeError, ValueError, KeyError):
            return None
