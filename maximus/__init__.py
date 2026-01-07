"""
Maximus - Python library for working with MAX messenger
Similar to Telethon but for MAX API through WebSocket
"""

from .client import MaxClient
from .types import Chat, Message, User, ChatType
from .session import Session
from . import events

__version__ = "0.1.0"
__all__ = ["MaxClient", "Chat", "Message", "User", "ChatType", "Session", "events"]

