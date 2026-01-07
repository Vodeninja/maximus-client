import time
from typing import Dict, Any


def create_nav_event(event_type: str, screen_to: int, screen_from: int = 51, action_id: int = None) -> Dict[str, Any]:
    if action_id is None:
        action_id = 1 if event_type == "COLD_START" else 2
    
    return {
        "type": "NAV",
        "userId": -1,
        "time": int(time.time() * 1000),
        "sessionId": int(time.time() * 1000) - 600,
        "event": event_type,
        "params": {
            "action_id": action_id,
            "screen_to": screen_to,
            "screen_from": screen_from,
            "prev_time": int(time.time() * 1000) - 600
        }
    }


def create_cold_start_event() -> Dict[str, Any]:
    return create_nav_event("COLD_START", 51, 51, 1)


def create_go_event(screen_to: int, screen_from: int = 51) -> Dict[str, Any]:
    return create_nav_event("GO", screen_to, screen_from, 2)

