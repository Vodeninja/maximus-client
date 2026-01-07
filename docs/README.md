# Maximus

Maximus is a Python library for working with MAX messenger API through WebSocket connections. It provides an asynchronous, event-driven interface similar to Telethon but specifically designed for MAX messenger.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [Events](#events)
- [Examples](#examples)
- [Advanced Usage](#advanced-usage)

## Installation

```bash
pip install maximus-client
```

## Quick Start

```python
import asyncio
from maximus import MaxClient

async def main():
    # Initialize client with session file
    client = MaxClient(session="my_session.maximus", debug=True)
    
    # Event handlers
    @client.on("ready")
    async def on_ready():
        print(f"Logged in as: {client.user.name}")
        print(f"Chats loaded: {len(client.chats)}")
    
    @client.on("new_message")
    async def on_message(message):
        print(f"[{message.chat_title}] {message.sender_name}: {message.text}")
        
        # Auto-reply example
        if message.text.lower() == "hello":
            await message.reply("Hello! How are you?")
    
    # Start the client
    await client.start(phone="YOUR_PHONE_NUMBER")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
```

## API Reference

### MaxClient

The main client class for interacting with MAX messenger.

#### Constructor

```python
MaxClient(
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

**Parameters:**
- `session` (str, optional): Path to session file. Defaults to "session.maximus"
- `device_id` (str, optional): Unique device identifier
- `user_agent` (str, optional): User agent string
- `app_version` (str, optional): Application version
- `device_type` (str): Device type. Default: "WEB"
- `locale` (str): Application locale. Default: "ru"
- `device_locale` (str): Device locale. Default: "ru"
- `os_version` (str): Operating system version. Default: "Windows"
- `device_name` (str): Device name. Default: "Chrome"
- `screen` (str): Screen resolution. Default: "1080x1920 1.0x"
- `timezone` (str): Timezone. Default: "Europe/Moscow"
- `version` (int): Protocol version. Default: 11
- `debug` (bool): Enable debug logging. Default: False

#### Methods

##### `async start(phone: str, code_callback: Callable = None)`

Start the client and authenticate.

**Parameters:**
- `phone` (str): Phone number for authentication
- `code_callback` (Callable, optional): Function to get verification code

**Example:**
```python
async def get_code():
    return input("Enter verification code: ")

await client.start(phone="+1234567890", code_callback=get_code)
```

##### `async connect()`

Alias for `start()` method.

##### `async disconnect()`

Disconnect from the server.

##### `async send_message(chat_id: int, text: str, reply_to: str = None) -> Message`

Send a message to a chat.

**Parameters:**
- `chat_id` (int): Target chat ID
- `text` (str): Message text
- `reply_to` (str, optional): ID of message to reply to

**Returns:** Message object (may be None)

##### `async edit_message(chat_id: int, message_id: str, text: str) -> Message`

Edit an existing message.

##### `async delete_message(chat_id: int, message_id: str)`

Delete a message.

##### `get_chats() -> List[Chat]`

Get all loaded chats.

##### `get_chat(chat_id: int) -> Chat`

Get a specific chat by ID.

##### `get_user(user_id: int) -> User`

Get a user by ID.

##### `get_entity(entity_id: int) -> Union[Chat, User]`

Get either a chat or user by ID.

##### `on(event_name: str)`

Decorator for registering event handlers.

**Example:**
```python
@client.on("new_message")
async def handle_message(message):
    print(f"New message: {message.text}")
```

##### `add_event_handler(event_name: str, handler: Callable)`

Add an event handler programmatically.

##### `remove_event_handler(event_name: str, handler: Callable)`

Remove an event handler.

##### `async run_until_disconnected()`

Keep the client running until manually disconnected.

#### Properties

- `user` (User): Current authenticated user
- `chats` (Dict[int, Chat]): Dictionary of loaded chats
- `users` (Dict[int, User]): Dictionary of loaded users
- `token` (str): Authentication token

### Chat

Represents a chat or dialog.

#### Properties

- `id` (int): Chat ID
- `type` (ChatType): Chat type (DIALOG or CHAT)
- `title` (str): Chat title
- `participants` (Dict[int, int]): Chat participants
- `last_message` (Message): Last message in chat
- `display_name` (str): Display name for the chat

#### Methods

##### `async send_message(text: str) -> Message`

Send a message to this chat.

##### `async reply(message: Message, text: str) -> Message`

Reply to a specific message in this chat.

### Message

Represents a message.

#### Properties

- `id` (str): Message ID
- `text` (str): Message text
- `sender` (int): Sender user ID
- `time` (int): Message timestamp
- `chat_id` (int): Chat ID where message was sent
- `type` (str): Message type
- `chat` (Chat): Chat object (if client is bound)
- `sender_user` (User): Sender user object (if client is bound)
- `sender_name` (str): Sender display name
- `chat_title` (str): Chat display name

#### Methods

##### `async reply(text: str) -> Message`

Reply to this message.

##### `async edit(text: str) -> Message`

Edit this message (if you're the sender).

### User

Represents a user.

#### Properties

- `id` (int): User ID
- `phone` (int): Phone number
- `name` (str): Display name
- `first_name` (str): First name
- `last_name` (str): Last name
- `photo_id` (int): Profile photo ID

## Events

The client supports various events that you can listen to:

### `ready`

Fired when the client is successfully authenticated and ready.

```python
@client.on("ready")
async def on_ready():
    print("Client is ready!")
```

### `new_message`

Fired when a new message is received.

```python
@client.on("new_message")
async def on_message(message: Message):
    print(f"New message from {message.sender_name}: {message.text}")
```

### `message_sent`

Fired when a message is successfully sent.

```python
@client.on("message_sent")
async def on_sent(message: Message):
    print(f"Message sent: {message.text}")
```

### `contacts_update`

Fired when contacts are updated.

```python
@client.on("contacts_update")
async def on_contacts(contacts: List[User]):
    print(f"Updated {len(contacts)} contacts")
```

### `auth_required`

Fired when re-authentication is required.

```python
@client.on("auth_required")
async def on_auth_required():
    print("Please re-authenticate")
```

### `auth_limit_exceeded`

Fired when authentication rate limit is exceeded.

```python
@client.on("auth_limit_exceeded")
async def on_limit(payload):
    print("Too many auth attempts, please wait")
```

### `auth_code_error`

Fired when there's an error with the verification code.

```python
@client.on("auth_code_error")
async def on_code_error(payload):
    print(f"Code error: {payload.get('localizedMessage')}")
```

## Examples

### Basic Bot

```python
import asyncio
from maximus import MaxClient

async def main():
    client = MaxClient(session="bot.maximus", debug=True)
    
    @client.on("ready")
    async def on_ready():
        print(f"Bot started as {client.user.name}")
    
    @client.on("new_message")
    async def on_message(message):
        # Ignore own messages
        if message.sender == client.user.id:
            return
        
        text = message.text.lower()
        
        if text == "/start":
            await message.reply("Hello! I'm a bot. Type /help for commands.")
        
        elif text == "/help":
            help_text = """
Available commands:
/start - Start the bot
/help - Show this help
/time - Get current time
/echo <text> - Echo your text
            """
            await message.reply(help_text)
        
        elif text == "/time":
            import datetime
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            await message.reply(f"Current time: {now}")
        
        elif text.startswith("/echo "):
            echo_text = text[6:]  # Remove "/echo "
            await message.reply(f"You said: {echo_text}")
    
    await client.start(phone="YOUR_BOT_PHONE")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
```

### Chat Management

```python
import asyncio
from maximus import MaxClient

async def main():
    client = MaxClient()
    
    @client.on("ready")
    async def on_ready():
        print("=== Chat List ===")
        for chat in client.get_chats():
            print(f"- {chat.display_name} (ID: {chat.id}, Type: {chat.type.value})")
            if chat.last_message:
                print(f"  Last: {chat.last_message.text[:50]}...")
    
    @client.on("new_message")
    async def on_message(message):
        # Log all messages
        print(f"[{message.chat_title}] {message.sender_name}: {message.text}")
        
        # Auto-moderate (example)
        if any(word in message.text.lower() for word in ["spam", "advertisement"]):
            await message.reply("⚠️ This message may contain spam.")
    
    await client.start(phone="YOUR_PHONE")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
```

### File Upload (when supported)

```python
# Note: File upload functionality depends on the MAX API capabilities
# This is a conceptual example

@client.on("new_message")
async def on_message(message):
    if message.text == "/upload":
        # This would be implemented when file upload is supported
        # await message.chat.send_file("path/to/file.jpg", caption="Here's your file!")
        await message.reply("File upload not yet implemented")
```

## Advanced Usage

### Custom Session Management

```python
from maximus import MaxClient

# Use custom session file location
client = MaxClient(session="/path/to/custom/session.maximus")

# Access session data
print(f"Session token: {client.session.token}")
print(f"Device ID: {client.session.device_id}")
```

### Error Handling

```python
import asyncio
from maximus import MaxClient

async def main():
    client = MaxClient(debug=True)
    
    @client.on("auth_code_error")
    async def on_code_error(payload):
        error = payload.get("error")
        message = payload.get("localizedMessage")
        
        if error == "error.limit.violate":
            print("Rate limited! Please wait before trying again.")
        else:
            print(f"Authentication error: {message}")
    
    @client.on("auth_required")
    async def on_auth_required():
        print("Re-authentication required. Please restart the client.")
    
    try:
        await client.start(phone="YOUR_PHONE")
        await client.run_until_disconnected()
    except Exception as e:
        print(f"Client error: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

### Multiple Clients

```python
import asyncio
from maximus import MaxClient

async def run_client(session_name, phone):
    client = MaxClient(session=f"{session_name}.maximus")
    
    @client.on("ready")
    async def on_ready():
        print(f"Client {session_name} ready as {client.user.name}")
    
    await client.start(phone=phone)
    return client

async def main():
    # Run multiple clients concurrently
    clients = await asyncio.gather(
        run_client("client1", "PHONE1"),
        run_client("client2", "PHONE2"),
    )
    
    # Keep all clients running
    await asyncio.gather(*[
        client.run_until_disconnected() for client in clients
    ])

if __name__ == "__main__":
    asyncio.run(main())
```

## Troubleshooting

### Common Issues

1. **Connection Issues**
   - Ensure stable internet connection
   - Check if MAX servers are accessible
   - Enable debug mode for detailed logs

2. **Authentication Problems**
   - Verify phone number format
   - Check verification code carefully
   - Clear session file if token is invalid

3. **Message Sending Fails**
   - Ensure client is connected and authenticated
   - Check chat permissions
   - Verify chat ID is correct

### Debug Mode

Enable debug mode to see detailed logs:

```python
client = MaxClient(debug=True)
```

This will show WebSocket messages, authentication steps, and other internal operations.

### Session Files

Session files store authentication tokens and device information. They are automatically created and managed by the library. If you encounter authentication issues, try deleting the session file to force re-authentication.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

MIT License - see LICENSE file for details.