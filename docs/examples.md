# Examples

This document contains practical examples of using the Maximus Client library.

## Table of Contents

- [Basic Examples](#basic-examples)
- [Bot Examples](#bot-examples)
- [Advanced Examples](#advanced-examples)
- [Error Handling](#error-handling)
- [Utility Examples](#utility-examples)

## Basic Examples

### Simple Client Setup

```python
import asyncio
from maximus import MaxClient

async def main():
    # Create client with debug enabled
    client = MaxClient(session="my_session.maximus", debug=True)
    
    # Simple ready handler
    @client.on("ready")
    async def on_ready():
        print(f"✅ Logged in as: {client.user.name}")
        print(f"📱 Phone: {client.user.phone}")
        print(f"💬 Loaded {len(client.chats)} chats")
    
    # Start client
    phone = input("Enter your phone number: ")
    
    async def get_code():
        return input("Enter verification code: ")
    
    await client.start(phone=phone, code_callback=get_code)
    
    # Keep running
    print("Client is running. Press Ctrl+C to stop.")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
```

### Message Echo Bot

```python
import asyncio
from maximus import MaxClient

async def main():
    client = MaxClient(session="echo_bot.maximus")
    
    @client.on("ready")
    async def on_ready():
        print("🤖 Echo Bot is ready!")
    
    @client.on("new_message")
    async def on_message(message):
        # Don't respond to own messages
        if message.sender == client.user.id:
            return
        
        # Echo the message back
        await message.reply(f"You said: {message.text}")
    
    await client.start(phone="YOUR_BOT_PHONE")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
```

### Chat List Viewer

```python
import asyncio
from maximus import MaxClient

async def main():
    client = MaxClient()
    
    @client.on("ready")
    async def on_ready():
        print("=== Your Chats ===")
        
        for chat in client.get_chats():
            print(f"\n📁 {chat.display_name}")
            print(f"   ID: {chat.id}")
            print(f"   Type: {chat.type.value}")
            print(f"   Participants: {len(chat.participants)}")
            
            if chat.last_message:
                last_msg = chat.last_message
                print(f"   Last message: {last_msg.sender_name}: {last_msg.text[:50]}...")
            else:
                print("   No messages")
    
    await client.start(phone="YOUR_PHONE")
    # Don't run forever, just show chats and exit
    await asyncio.sleep(2)
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

## Bot Examples

### Command Bot

```python
import asyncio
import datetime
import random
from maximus import MaxClient

class CommandBot:
    def __init__(self, phone: str):
        self.client = MaxClient(session="command_bot.maximus")
        self.phone = phone
        self.commands = {
            "/start": self.cmd_start,
            "/help": self.cmd_help,
            "/time": self.cmd_time,
            "/random": self.cmd_random,
            "/info": self.cmd_info,
            "/echo": self.cmd_echo,
        }
    
    async def start(self):
        @self.client.on("ready")
        async def on_ready():
            print(f"🤖 Command Bot started as {self.client.user.name}")
        
        @self.client.on("new_message")
        async def on_message(message):
            await self.handle_message(message)
        
        await self.client.start(phone=self.phone)
        await self.client.run_until_disconnected()
    
    async def handle_message(self, message):
        # Ignore own messages
        if message.sender == self.client.user.id:
            return
        
        text = message.text.strip()
        
        # Handle commands
        if text.startswith("/"):
            parts = text.split(" ", 1)
            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""
            
            if command in self.commands:
                await self.commands[command](message, args)
            else:
                await message.reply("❓ Unknown command. Type /help for available commands.")
    
    async def cmd_start(self, message, args):
        welcome = """
🤖 Welcome to Command Bot!

I can help you with various tasks. Type /help to see available commands.
        """
        await message.reply(welcome.strip())
    
    async def cmd_help(self, message, args):
        help_text = """
📋 Available Commands:

/start - Show welcome message
/help - Show this help
/time - Get current time
/random [max] - Get random number (default max: 100)
/info - Get chat information
/echo <text> - Echo your text
        """
        await message.reply(help_text.strip())
    
    async def cmd_time(self, message, args):
        now = datetime.datetime.now()
        time_str = now.strftime("%Y-%m-%d %H:%M:%S")
        await message.reply(f"🕐 Current time: {time_str}")
    
    async def cmd_random(self, message, args):
        try:
            max_num = int(args) if args else 100
            if max_num <= 0:
                await message.reply("❌ Please provide a positive number.")
                return
            
            num = random.randint(1, max_num)
            await message.reply(f"🎲 Random number (1-{max_num}): {num}")
        except ValueError:
            await message.reply("❌ Please provide a valid number.")
    
    async def cmd_info(self, message, args):
        chat = message.chat
        if not chat:
            await message.reply("❌ Could not get chat information.")
            return
        
        info = f"""
📊 Chat Information:

Name: {chat.display_name}
ID: {chat.id}
Type: {chat.type.value}
Participants: {len(chat.participants)}
Status: {chat.status}
        """
        await message.reply(info.strip())
    
    async def cmd_echo(self, message, args):
        if not args:
            await message.reply("❌ Please provide text to echo. Usage: /echo <text>")
            return
        
        await message.reply(f"🔊 {args}")

async def main():
    bot = CommandBot("YOUR_BOT_PHONE")
    await bot.start()

if __name__ == "__main__":
    asyncio.run(main())
```

### Auto-Reply Bot

```python
import asyncio
import re
from maximus import MaxClient

class AutoReplyBot:
    def __init__(self, phone: str):
        self.client = MaxClient(session="autoreply_bot.maximus")
        self.phone = phone
        
        # Auto-reply patterns
        self.replies = {
            r"hello|hi|hey": "Hello! How can I help you?",
            r"how are you": "I'm doing great, thank you for asking!",
            r"what.*time": "You can check the time with /time command.",
            r"thank you|thanks": "You're welcome! 😊",
            r"bye|goodbye": "Goodbye! Have a great day!",
            r"help": "Type /help to see available commands.",
        }
    
    async def start(self):
        @self.client.on("ready")
        async def on_ready():
            print(f"🤖 Auto-Reply Bot started as {self.client.user.name}")
        
        @self.client.on("new_message")
        async def on_message(message):
            await self.handle_message(message)
        
        await self.client.start(phone=self.phone)
        await self.client.run_until_disconnected()
    
    async def handle_message(self, message):
        # Ignore own messages
        if message.sender == self.client.user.id:
            return
        
        text = message.text.lower().strip()
        
        # Check for auto-reply patterns
        for pattern, reply in self.replies.items():
            if re.search(pattern, text):
                await message.reply(reply)
                break

async def main():
    bot = AutoReplyBot("YOUR_BOT_PHONE")
    await bot.start()

if __name__ == "__main__":
    asyncio.run(main())
```

## Advanced Examples

### Multi-Client Manager

```python
import asyncio
from maximus import MaxClient
from typing import Dict, List

class MultiClientManager:
    def __init__(self):
        self.clients: Dict[str, MaxClient] = {}
        self.running = False
    
    async def add_client(self, name: str, phone: str, session_file: str = None):
        """Add a new client to the manager."""
        if session_file is None:
            session_file = f"{name}.maximus"
        
        client = MaxClient(session=session_file, debug=True)
        
        @client.on("ready")
        async def on_ready():
            print(f"✅ Client '{name}' ready as {client.user.name}")
        
        @client.on("new_message")
        async def on_message(message):
            print(f"[{name}] {message.chat_title}: {message.sender_name}: {message.text}")
        
        self.clients[name] = client
        
        # Start the client
        await client.start(phone=phone)
        print(f"🚀 Client '{name}' started")
    
    async def send_to_all(self, chat_id: int, text: str):
        """Send a message from all clients to a specific chat."""
        tasks = []
        for name, client in self.clients.items():
            task = client.send_message(chat_id, f"[{name}] {text}")
            tasks.append(task)
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def broadcast_to_all_chats(self, text: str):
        """Broadcast a message to all chats from all clients."""
        for name, client in self.clients.items():
            for chat in client.get_chats():
                try:
                    await chat.send_message(f"[Broadcast from {name}] {text}")
                    await asyncio.sleep(0.1)  # Rate limiting
                except Exception as e:
                    print(f"Failed to send to {chat.display_name}: {e}")
    
    async def run_all(self):
        """Keep all clients running."""
        self.running = True
        tasks = []
        
        for name, client in self.clients.items():
            task = asyncio.create_task(client.run_until_disconnected())
            tasks.append(task)
        
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            print("Stopping all clients...")
            await self.stop_all()
    
    async def stop_all(self):
        """Stop all clients."""
        self.running = False
        for name, client in self.clients.items():
            try:
                await client.disconnect()
                print(f"🛑 Client '{name}' stopped")
            except Exception as e:
                print(f"Error stopping client '{name}': {e}")

async def main():
    manager = MultiClientManager()
    
    # Add multiple clients
    await manager.add_client("bot1", "PHONE1")
    await manager.add_client("bot2", "PHONE2")
    
    # Example: Send message from all clients
    # await manager.send_to_all(12345, "Hello from all bots!")
    
    # Keep all clients running
    await manager.run_all()

if __name__ == "__main__":
    asyncio.run(main())
```

### Message Logger

```python
import asyncio
import json
import datetime
from pathlib import Path
from maximus import MaxClient

class MessageLogger:
    def __init__(self, phone: str, log_dir: str = "logs"):
        self.client = MaxClient(session="logger.maximus")
        self.phone = phone
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
    
    async def start(self):
        @self.client.on("ready")
        async def on_ready():
            print(f"📝 Message Logger started as {self.client.user.name}")
            print(f"📁 Logs will be saved to: {self.log_dir.absolute()}")
        
        @self.client.on("new_message")
        async def on_message(message):
            await self.log_message(message)
        
        await self.client.start(phone=self.phone)
        await self.client.run_until_disconnected()
    
    async def log_message(self, message):
        """Log a message to a JSON file."""
        try:
            # Create log entry
            log_entry = {
                "timestamp": datetime.datetime.now().isoformat(),
                "message_id": message.id,
                "chat_id": message.chat_id,
                "chat_title": message.chat_title,
                "sender_id": message.sender,
                "sender_name": message.sender_name,
                "text": message.text,
                "message_time": message.time,
                "type": message.type,
                "has_attachments": len(message.attaches) > 0
            }
            
            # Determine log file (one per chat per day)
            date_str = datetime.datetime.now().strftime("%Y-%m-%d")
            log_file = self.log_dir / f"chat_{message.chat_id}_{date_str}.jsonl"
            
            # Append to log file
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            
            print(f"📝 Logged message from {message.sender_name} in {message.chat_title}")
            
        except Exception as e:
            print(f"❌ Error logging message: {e}")
    
    def get_chat_logs(self, chat_id: int, date: str = None) -> List[dict]:
        """Get logs for a specific chat and date."""
        if date is None:
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        log_file = self.log_dir / f"chat_{chat_id}_{date}.jsonl"
        
        if not log_file.exists():
            return []
        
        logs = []
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    logs.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
        
        return logs
    
    def search_logs(self, query: str, chat_id: int = None) -> List[dict]:
        """Search for messages containing specific text."""
        results = []
        
        # Search in all log files
        for log_file in self.log_dir.glob("*.jsonl"):
            # Filter by chat if specified
            if chat_id is not None:
                if f"chat_{chat_id}_" not in log_file.name:
                    continue
            
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        if query.lower() in entry["text"].lower():
                            results.append(entry)
                    except (json.JSONDecodeError, KeyError):
                        continue
        
        return results

async def main():
    logger = MessageLogger("YOUR_PHONE")
    await logger.start()

if __name__ == "__main__":
    asyncio.run(main())
```

## Error Handling

### Robust Client with Reconnection

```python
import asyncio
import logging
from maximus import MaxClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RobustClient:
    def __init__(self, phone: str, session: str = "robust.maximus"):
        self.phone = phone
        self.session = session
        self.client = None
        self.running = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
    
    async def start(self):
        """Start the client with error handling."""
        self.running = True
        
        while self.running:
            try:
                await self._create_client()
                await self._run_client()
            except Exception as e:
                logger.error(f"Client error: {e}")
                await self._handle_error()
            
            if self.running:
                await asyncio.sleep(5)  # Wait before reconnecting
    
    async def _create_client(self):
        """Create and configure the client."""
        self.client = MaxClient(session=self.session, debug=True)
        
        @self.client.on("ready")
        async def on_ready():
            logger.info(f"✅ Connected as {self.client.user.name}")
            self.reconnect_attempts = 0  # Reset counter on successful connection
        
        @self.client.on("new_message")
        async def on_message(message):
            try:
                await self._handle_message(message)
            except Exception as e:
                logger.error(f"Error handling message: {e}")
        
        @self.client.on("auth_required")
        async def on_auth_required():
            logger.warning("Re-authentication required")
        
        @self.client.on("auth_code_error")
        async def on_code_error(payload):
            logger.error(f"Auth code error: {payload.get('localizedMessage')}")
    
    async def _run_client(self):
        """Run the client."""
        async def get_code():
            return input("Enter verification code: ")
        
        await self.client.start(phone=self.phone, code_callback=get_code)
        await self.client.run_until_disconnected()
    
    async def _handle_message(self, message):
        """Handle incoming messages."""
        # Ignore own messages
        if message.sender == self.client.user.id:
            return
        
        logger.info(f"Message from {message.sender_name}: {message.text}")
        
        # Simple echo for testing
        if message.text.lower() == "ping":
            await message.reply("pong")
    
    async def _handle_error(self):
        """Handle errors and decide whether to reconnect."""
        self.reconnect_attempts += 1
        
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            logger.error(f"Max reconnection attempts ({self.max_reconnect_attempts}) reached. Stopping.")
            self.running = False
            return
        
        logger.warning(f"Reconnection attempt {self.reconnect_attempts}/{self.max_reconnect_attempts}")
        
        # Clean up current client
        if self.client:
            try:
                await self.client.disconnect()
            except:
                pass
            self.client = None
    
    async def stop(self):
        """Stop the client gracefully."""
        logger.info("Stopping client...")
        self.running = False
        
        if self.client:
            try:
                await self.client.disconnect()
            except Exception as e:
                logger.error(f"Error during disconnect: {e}")

async def main():
    client = RobustClient("YOUR_PHONE")
    
    try:
        await client.start()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    finally:
        await client.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

## Utility Examples

### Contact Exporter

```python
import asyncio
import json
from maximus import MaxClient

async def export_contacts(phone: str, output_file: str = "contacts.json"):
    """Export all contacts to a JSON file."""
    client = MaxClient(session="exporter.maximus")
    
    contacts_data = []
    
    @client.on("ready")
    async def on_ready():
        print(f"📱 Connected as {client.user.name}")
        print(f"👥 Found {len(client.users)} users")
        
        # Export user data
        for user in client.users.values():
            contact_info = {
                "id": user.id,
                "name": user.name,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone": user.phone,
            }
            contacts_data.append(contact_info)
        
        # Save to file
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(contacts_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Exported {len(contacts_data)} contacts to {output_file}")
        await client.disconnect()
    
    await client.start(phone=phone)

async def main():
    await export_contacts("YOUR_PHONE", "my_contacts.json")

if __name__ == "__main__":
    asyncio.run(main())
```

### Chat Statistics

```python
import asyncio
from collections import defaultdict, Counter
from maximus import MaxClient

class ChatStatistics:
    def __init__(self, phone: str):
        self.client = MaxClient(session="stats.maximus")
        self.phone = phone
        self.message_count = defaultdict(int)
        self.user_message_count = defaultdict(int)
        self.word_count = Counter()
    
    async def start(self):
        @self.client.on("ready")
        async def on_ready():
            print(f"📊 Statistics collector started as {self.client.user.name}")
            await self.analyze_chats()
        
        @self.client.on("new_message")
        async def on_message(message):
            await self.process_message(message)
        
        await self.client.start(phone=self.phone)
        await self.client.run_until_disconnected()
    
    async def analyze_chats(self):
        """Analyze existing chats."""
        print("\n=== Chat Analysis ===")
        
        for chat in self.client.get_chats():
            print(f"\n📁 {chat.display_name}")
            print(f"   Type: {chat.type.value}")
            print(f"   Participants: {len(chat.participants)}")
            
            if chat.last_message:
                last_msg = chat.last_message
                print(f"   Last message: {last_msg.sender_name} - {last_msg.text[:50]}...")
        
        print(f"\n📈 Total chats: {len(self.client.chats)}")
        print(f"👥 Total users: {len(self.client.users)}")
    
    async def process_message(self, message):
        """Process a new message for statistics."""
        # Count messages per chat
        self.message_count[message.chat_id] += 1
        
        # Count messages per user
        self.user_message_count[message.sender] += 1
        
        # Count words
        words = message.text.lower().split()
        self.word_count.update(words)
        
        # Print live stats every 10 messages
        total_messages = sum(self.message_count.values())
        if total_messages % 10 == 0:
            await self.print_stats()
    
    async def print_stats(self):
        """Print current statistics."""
        print("\n=== Live Statistics ===")
        
        # Most active chats
        print("\n🔥 Most active chats:")
        for chat_id, count in sorted(self.message_count.items(), key=lambda x: x[1], reverse=True)[:5]:
            chat = self.client.get_chat(chat_id)
            chat_name = chat.display_name if chat else f"Chat {chat_id}"
            print(f"   {chat_name}: {count} messages")
        
        # Most active users
        print("\n👤 Most active users:")
        for user_id, count in sorted(self.user_message_count.items(), key=lambda x: x[1], reverse=True)[:5]:
            user = self.client.get_user(user_id)
            user_name = user.name if user else f"User {user_id}"
            print(f"   {user_name}: {count} messages")
        
        # Most common words
        print("\n💬 Most common words:")
        for word, count in self.word_count.most_common(10):
            if len(word) > 2:  # Skip short words
                print(f"   {word}: {count}")

async def main():
    stats = ChatStatistics("YOUR_PHONE")
    await stats.start()

if __name__ == "__main__":
    asyncio.run(main())
```

These examples demonstrate various use cases and patterns for the Maximus Client library. You can adapt and combine them to create more complex applications.