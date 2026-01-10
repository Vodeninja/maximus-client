# Maximus Client

Modern framework for MAX messenger with clean architecture and full functionality.

## Features

- **Clean Public API** - Only essential classes exposed
- **Proper Type Hints** - Full type safety with no `Any` types
- **Modern Architecture** - Based on proven patterns from maxo framework
- **Full MAX API Support** - Messages, stickers, reactions, chats, contacts
- **Session Management** - File-based session storage
- **Event System** - Comprehensive event handling
- **Auto-reconnection** - Automatic connection recovery
- **Debug Mode** - Detailed logging for development

## Installation

```bash
pip install maximus-client

# With Redis support
pip install maximus-client[redis]

# With all optional dependencies  
pip install maximus-client[all]
```

## Quick Start

```python
import asyncio
from maximus import MaxClient

async def main():
    client = MaxClient(session="session.maximus", debug=True)
    
    @client.on("ready")
    async def on_ready():
        print("Bot is ready!")
        print(f"User: {client.user.name}")
        print(f"Chats: {len(client.chats)}")
    
    @client.on("new_message")
    async def on_message(message):
        print(f"{message.sender_name}: {message.text}")
        
        if message.text.lower() == "hello":
            await message.reply("Hello! How are you?")
        
        if message.text.lower() == "sticker":
            await message.reply_sticker(80382389)
        
        if message.text.lower() == "like":
            await message.react("👍")
    
    async def code_callback():
        return input("Enter confirmation code: ")
    
    await client.start(
        phone="+1234567890",
        code_callback=code_callback
    )
    
    await client.run_until_disconnected()

asyncio.run(main())
```

## Architecture

### Public API
- `MaxClient` - Main client class
- Type-safe models: `Chat`, `Message`, `User`, `ChatType`
- Proper exception hierarchy: `MaximusError`, `AuthError`, `ConnectionError`

### Clean Structure
```
src/maximus/
├── __init__.py          # Public API
├── client.py            # Main client
├── types/               # Type definitions
├── errors/              # Exception hierarchy
└── _internal/           # Private implementation
```

## Full API Reference

### MaxClient

```python
MaxClient(
    session: Optional[str] = None,           # Session file path
    device_id: Optional[str] = None,         # Device ID
    user_agent: Optional[str] = None,        # User agent
    app_version: Optional[str] = None,       # App version
    device_type: str = "ANDROID",            # Device type
    locale: str = "ru",                      # Locale
    device_locale: str = "ru",               # Device locale
    os_version: str = "Windows",             # OS version
    device_name: str = "Chrome",             # Device name
    screen: str = "1080x1920 1.0x",          # Screen resolution
    timezone: str = "Europe/Moscow",         # Timezone
    version: int = 11,                       # Protocol version
    debug: bool = False                      # Debug mode
)
```

#### Methods

- `start(phone, code_callback)` - Start client and authenticate
- `disconnect()` - Disconnect from API
- `send_message(chat_id, text, reply_to=None)` - Send text message
- `send_sticker(chat_id, sticker_id, reply_to=None)` - Send sticker
- `send_reaction(chat_id, message_id, reaction="👍")` - Send reaction
- `edit_message(chat_id, message_id, text)` - Edit message
- `delete_message(chat_id, message_id)` - Delete message
- `get_chats()` - Get list of chats
- `get_chat(chat_id)` - Get specific chat
- `get_user(user_id)` - Get user info
- `get_entity(entity_id)` - Get chat or user
- `on(event_name)` - Decorator for event handlers
- `run_until_disconnected()` - Keep running until interrupted

#### Properties

- `user: Optional[User]` - Current user
- `chats: Dict[int, Chat]` - All chats

#### Events

- `ready` - Fired when client is ready
- `new_message` - New message received
- `contacts_update` - Contacts updated
- `message_sent` - Message sent successfully
- `auth_required` - Authentication required
- `auth_limit_exceeded` - Too many auth attempts
- `auth_code_error` - Auth code error

### Message

```python
class Message:
    id: str                    # Message ID
    text: str                  # Message text
    sender: int                # Sender user ID
    time: int                  # Timestamp
    chat_id: int              # Chat ID
    type: str                 # Message type
    attaches: List[Dict]      # Attachments
    
    # Properties
    chat: Optional[Chat]       # Chat object
    sender_user: Optional[User] # Sender user object
    sender_name: str          # Sender display name
    chat_title: str           # Chat display name
    
    # Methods
    async def reply(text: str) -> Optional[Message]
    async def reply_sticker(sticker_id: int) -> Optional[Message]
    async def react(reaction: str = "👍") -> None
    async def edit(text: str) -> Optional[Message]
```

### Chat

```python
class Chat:
    id: int                           # Chat ID
    type: ChatType                    # Chat type (DIALOG/CHAT)
    title: Optional[str]              # Chat title
    participants: Dict[int, int]      # Participants
    last_message: Optional[Message]   # Last message
    owner: Optional[int]              # Owner ID
    created: Optional[int]            # Creation time
    modified: Optional[int]           # Modification time
    status: str                       # Chat status
    
    # Properties
    display_name: str                 # Display name
    
    # Methods
    async def send_message(text: str) -> Optional[Message]
    async def send_sticker(sticker_id: int) -> Optional[Message]
    async def reply(message: Message, text: str) -> Optional[Message]
    async def reply_sticker(message: Message, sticker_id: int) -> Optional[Message]
    async def react_to_message(message_id: str, reaction: str = "👍") -> None
```

### User

```python
class User:
    id: int                    # User ID
    phone: Optional[int]       # Phone number
    name: Optional[str]        # Display name
    first_name: Optional[str]  # First name
    last_name: Optional[str]   # Last name
    photo_id: Optional[int]    # Photo ID
    base_url: Optional[str]    # Base URL
```

## Session Management

Sessions are stored in JSON files (default: `session.maximus`):

```json
{
  "device_id": "uuid4-generated",
  "user_agent": "Mozilla/5.0...",
  "app_version": "25.12.3",
  "device_type": "ANDROID",
  "locale": "ru",
  "token": "auth_token_here",
  "phone": "+1234567890"
}
```

## Error Handling

```python
from maximus.errors import MaximusError, AuthError, ConnectionError

try:
    await client.start(phone="+1234567890", code_callback=code_callback)
except AuthError as e:
    print(f"Authentication failed: {e}")
except ConnectionError as e:
    print(f"Connection failed: {e}")
except MaximusError as e:
    print(f"General error: {e}")
```

## Type Safety

All APIs are fully typed:

```python
from maximus import MaxClient
from maximus.types import Message, Chat, User, ChatType

client: MaxClient = MaxClient()
message: Message = ...
chat: Chat = message.chat
user: User = message.sender_user
chat_type: ChatType = chat.type
```