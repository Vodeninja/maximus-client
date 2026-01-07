# API Reference

Complete API reference for Maximus Client library.

## Classes

### MaxClient

Main client class for interacting with MAX messenger.

```python
class MaxClient:
    def __init__(
        self,
        session: Optional[str] = None,
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
        version: int = 11,
        debug: bool = False
    )
```

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `user` | `Optional[User]` | Current authenticated user |
| `chats` | `Dict[int, Chat]` | Dictionary of loaded chats |
| `users` | `Dict[int, User]` | Dictionary of loaded users |
| `token` | `Optional[str]` | Authentication token |
| `session` | `Session` | Session management object |
| `connection` | `MaximusConnection` | WebSocket connection handler |

#### Methods

##### Authentication Methods

###### `async start(phone: Optional[str] = None, code_callback: Optional[Callable] = None)`

Start the client and authenticate.

**Parameters:**
- `phone` (str, optional): Phone number for authentication
- `code_callback` (Callable, optional): Async function to get verification code

**Raises:**
- `RuntimeError`: If connection fails
- `ValueError`: If phone number is invalid

**Example:**
```python
async def get_verification_code():
    return input("Enter code: ")

await client.start(
    phone="+1234567890",
    code_callback=get_verification_code
)
```

###### `async connect()`

Alias for `start()` method without parameters.

###### `async disconnect()`

Disconnect from the server and cleanup resources.

##### Message Methods

###### `async send_message(chat_id: int, text: str, reply_to: Optional[str] = None) -> Optional[Message]`

Send a message to a chat.

**Parameters:**
- `chat_id` (int): Target chat ID
- `text` (str): Message text (max length depends on server limits)
- `reply_to` (str, optional): ID of message to reply to

**Returns:** `Optional[Message]` - Message object or None

**Raises:**
- `RuntimeError`: If client is not connected
- `ValueError`: If chat_id is invalid

**Example:**
```python
# Send simple message
await client.send_message(12345, "Hello, world!")

# Reply to a message
await client.send_message(12345, "Thanks!", reply_to="msg_123")
```

###### `async edit_message(chat_id: int, message_id: str, text: str) -> Optional[Message]`

Edit an existing message.

**Parameters:**
- `chat_id` (int): Chat ID where message exists
- `message_id` (str): ID of message to edit
- `text` (str): New message text

**Returns:** `Optional[Message]` - Updated message object or None

**Note:** You can only edit your own messages.

###### `async delete_message(chat_id: int, message_id: str)`

Delete a message.

**Parameters:**
- `chat_id` (int): Chat ID where message exists
- `message_id` (str): ID of message to delete

**Note:** You can only delete your own messages or messages in chats where you have admin rights.

##### Data Access Methods

###### `get_chats() -> List[Chat]`

Get all loaded chats.

**Returns:** `List[Chat]` - List of all chats

###### `get_chat(chat_id: int) -> Optional[Chat]`

Get a specific chat by ID.

**Parameters:**
- `chat_id` (int): Chat ID to retrieve

**Returns:** `Optional[Chat]` - Chat object or None if not found

###### `get_user(user_id: int) -> Optional[User]`

Get a user by ID.

**Parameters:**
- `user_id` (int): User ID to retrieve

**Returns:** `Optional[User]` - User object or None if not found

###### `get_entity(entity_id: int) -> Optional[Union[Chat, User]]`

Get either a chat or user by ID.

**Parameters:**
- `entity_id` (int): Entity ID to retrieve

**Returns:** `Optional[Union[Chat, User]]` - Chat or User object, or None

##### Iterator Methods

###### `iter_chats()`

Get an iterator over all chats.

**Returns:** `Iterator[Chat]`

**Example:**
```python
for chat in client.iter_chats():
    print(f"Chat: {chat.display_name}")
```

###### `iter_users()`

Get an iterator over all users.

**Returns:** `Iterator[User]`

##### Event Methods

###### `on(event_name: str)`

Decorator for registering event handlers.

**Parameters:**
- `event_name` (str): Name of event to listen for

**Returns:** Decorator function

**Example:**
```python
@client.on("new_message")
async def handle_message(message):
    print(f"Received: {message.text}")
```

###### `add_event_handler(event_name: str, handler: Callable)`

Add an event handler programmatically.

**Parameters:**
- `event_name` (str): Name of event to listen for
- `handler` (Callable): Function to handle the event

**Example:**
```python
async def my_handler(message):
    print(f"Message: {message.text}")

client.add_event_handler("new_message", my_handler)
```

###### `remove_event_handler(event_name: str, handler: Callable)`

Remove an event handler.

**Parameters:**
- `event_name` (str): Name of event
- `handler` (Callable): Handler function to remove

##### Utility Methods

###### `async run_until_disconnected()`

Keep the client running until manually disconnected.

**Note:** This method will run indefinitely until the client is disconnected or an exception occurs.

**Example:**
```python
try:
    await client.run_until_disconnected()
except KeyboardInterrupt:
    print("Client stopped by user")
```

### Chat

Represents a chat or dialog in MAX messenger.

```python
@dataclass
class Chat:
    id: int
    type: ChatType
    title: Optional[str] = None
    participants: Dict[int, int] = None
    last_message: Optional[Message] = None
    owner: Optional[int] = None
    created: Optional[int] = None
    modified: Optional[int] = None
    status: str = "ACTIVE"
```

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `id` | `int` | Unique chat identifier |
| `type` | `ChatType` | Chat type (DIALOG or CHAT) |
| `title` | `Optional[str]` | Chat title/name |
| `participants` | `Dict[int, int]` | Dictionary of participant IDs |
| `last_message` | `Optional[Message]` | Last message in chat |
| `owner` | `Optional[int]` | Chat owner user ID |
| `created` | `Optional[int]` | Creation timestamp |
| `modified` | `Optional[int]` | Last modification timestamp |
| `status` | `str` | Chat status (ACTIVE, etc.) |
| `display_name` | `str` | Display name for the chat |

#### Methods

##### `async send_message(text: str) -> Optional[Message]`

Send a message to this chat.

**Parameters:**
- `text` (str): Message text

**Returns:** `Optional[Message]` - Sent message object

**Raises:**
- `RuntimeError`: If chat is not bound to a client

##### `async reply(message: Message, text: str) -> Optional[Message]`

Reply to a specific message in this chat.

**Parameters:**
- `message` (Message): Message to reply to
- `text` (str): Reply text

**Returns:** `Optional[Message]` - Reply message object

#### Class Methods

##### `from_dict(data: Dict[str, Any], client: Optional[Any] = None) -> "Chat"`

Create a Chat object from dictionary data.

**Parameters:**
- `data` (Dict): Raw chat data from API
- `client` (Optional): Client instance to bind to

**Returns:** `Chat` - New Chat object

### Message

Represents a message in MAX messenger.

```python
@dataclass
class Message:
    id: str
    text: str
    sender: int
    time: int
    chat_id: int
    type: str = "USER"
    attaches: List[Dict[str, Any]] = None
```

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `id` | `str` | Unique message identifier |
| `text` | `str` | Message text content |
| `sender` | `int` | Sender user ID |
| `time` | `int` | Message timestamp |
| `chat_id` | `int` | Chat ID where message was sent |
| `type` | `str` | Message type (USER, SYSTEM, etc.) |
| `attaches` | `List[Dict]` | List of attachments |
| `chat` | `Optional[Chat]` | Chat object (if client bound) |
| `sender_user` | `Optional[User]` | Sender user object (if client bound) |
| `sender_name` | `str` | Display name of sender |
| `chat_title` | `str` | Display name of chat |

#### Methods

##### `async reply(text: str) -> Optional[Message]`

Reply to this message.

**Parameters:**
- `text` (str): Reply text

**Returns:** `Optional[Message]` - Reply message object

**Raises:**
- `RuntimeError`: If message is not bound to a client

##### `async edit(text: str) -> Optional[Message]`

Edit this message (if you're the sender).

**Parameters:**
- `text` (str): New message text

**Returns:** `Optional[Message]` - Updated message object

**Raises:**
- `RuntimeError`: If message is not bound to a client

#### Class Methods

##### `from_dict(data: Dict[str, Any], chat_id: int, client: Optional[Any] = None) -> "Message"`

Create a Message object from dictionary data.

**Parameters:**
- `data` (Dict): Raw message data from API
- `chat_id` (int): Chat ID where message belongs
- `client` (Optional): Client instance to bind to

**Returns:** `Message` - New Message object

### User

Represents a user in MAX messenger.

```python
@dataclass
class User:
    id: int
    phone: Optional[int] = None
    name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    photo_id: Optional[int] = None
    base_url: Optional[str] = None
    options: List[str] = None
```

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `id` | `int` | Unique user identifier |
| `phone` | `Optional[int]` | User's phone number |
| `name` | `Optional[str]` | Display name |
| `first_name` | `Optional[str]` | First name |
| `last_name` | `Optional[str]` | Last name |
| `photo_id` | `Optional[int]` | Profile photo ID |
| `base_url` | `Optional[str]` | Base URL for resources |
| `options` | `List[str]` | User options/flags |

#### Class Methods

##### `from_dict(data: Dict[str, Any]) -> "User"`

Create a User object from dictionary data.

**Parameters:**
- `data` (Dict): Raw user data from API

**Returns:** `User` - New User object

### ChatType

Enumeration of chat types.

```python
class ChatType(Enum):
    DIALOG = "DIALOG"  # Private conversation
    CHAT = "CHAT"      # Group chat
```

## Events

### Event Types

| Event Name | Parameters | Description |
|------------|------------|-------------|
| `ready` | None | Client is authenticated and ready |
| `new_message` | `message: Message` | New message received |
| `message_sent` | `message: Message` | Message successfully sent |
| `contacts_update` | `contacts: List[User]` | Contacts were updated |
| `auth_required` | None | Re-authentication required |
| `auth_limit_exceeded` | `payload: Dict` | Auth rate limit exceeded |
| `auth_code_error` | `payload: Dict` | Verification code error |

### Event Handler Signatures

```python
# Ready event
@client.on("ready")
async def on_ready():
    pass

# New message event
@client.on("new_message")
async def on_message(message: Message):
    pass

# Message sent event
@client.on("message_sent")
async def on_sent(message: Message):
    pass

# Contacts update event
@client.on("contacts_update")
async def on_contacts(contacts: List[User]):
    pass

# Auth required event
@client.on("auth_required")
async def on_auth_required():
    pass

# Auth limit exceeded event
@client.on("auth_limit_exceeded")
async def on_limit(payload: Dict[str, Any]):
    pass

# Auth code error event
@client.on("auth_code_error")
async def on_code_error(payload: Dict[str, Any]):
    pass
```

## Exceptions

The library may raise the following exceptions:

- `RuntimeError`: General runtime errors (connection issues, unbound objects)
- `ValueError`: Invalid parameter values
- `asyncio.TimeoutError`: Operation timeout
- `ConnectionError`: Network connection issues

## Type Hints

The library is fully typed and supports type checking with mypy and other type checkers.

```python
from typing import Optional, List, Dict, Any, Callable
from maximus import MaxClient, Chat, Message, User, ChatType
```