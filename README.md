# Maximus Client

Python library for working with MAX messenger API through WebSocket connections.

## Installation

```bash
pip install maximus-client
```

## Quick Start

```python
import asyncio
from maximus import MaxClient

async def main():
    client = MaxClient(session="session.maximus", debug=True)
    
    @client.on("ready")
    async def on_ready():
        print("Authorization successful!")
        print(f"User: {client.user.name if client.user else 'Unknown'}")
        print(f"Chats: {len(client.chats)}")
    
    @client.on("new_message")
    async def on_new_message(message):
        print(f"[{message.chat_title}] {message.sender_name}: {message.text}")
        
        if message.text.lower() == "hello":
            await message.reply("Hello! How are you?")
    
    phone_number = "YOUR_PHONE_NUMBER"
    await client.start(phone=phone_number)
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
```

## Features

- Asynchronous WebSocket-based communication
- Event-driven architecture
- Session management
- Message handling and sending
- Contact management
- Chat operations

## Documentation

- [Complete Documentation](docs/README.md)
- [API Reference](docs/api-reference.md)
- [Examples](docs/examples.md)

## Requirements

- Python 3.8+
- websockets>=12.0
- sqlalchemy>=2.0.0

## License

MIT License