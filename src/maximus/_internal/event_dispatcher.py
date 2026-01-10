import asyncio
from typing import Callable, List, Dict, Any
from .interfaces import IEventDispatcher
from .constants import call_handlers


class EventDispatcher(IEventDispatcher):
    """Event dispatcher implementation."""
    
    def __init__(self) -> None:
        self._event_handlers: Dict[str, List[Callable]] = {}
    
    def on(self, event_type: str) -> Callable:
        """Decorator for event handlers."""
        def decorator(func: Callable) -> Callable:
            self.add_event_handler(event_type, func)
            return func
        return decorator
    
    def add_event_handler(self, event_name: str, handler: Callable) -> None:
        """Add event handler."""
        if event_name not in self._event_handlers:
            self._event_handlers[event_name] = []
        self._event_handlers[event_name].append(handler)
    
    def remove_event_handler(self, event_name: str, handler: Callable) -> None:
        """Remove event handler."""
        if event_name in self._event_handlers:
            if handler in self._event_handlers[event_name]:
                self._event_handlers[event_name].remove(handler)
    
    async def dispatch_event(self, event_name: str, *args, **kwargs) -> None:
        """Dispatch event to handlers."""
        if event_name in self._event_handlers:
            await call_handlers(self._event_handlers[event_name], *args, **kwargs)