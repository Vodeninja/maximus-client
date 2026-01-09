import asyncio
from maximus import MaxClient
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    client = MaxClient(session="session.maximus", debug=True)
    
    @client.on("ready")
    async def on_ready():
        print("Authorization successful!")
        print(f"User: {client.user.name if client.user else 'Unknown'}")
        print(f"Chats: {len(client.chats)}")
        for chat in client.get_chats():
            print(f"  - {chat.title or f'Chat {chat.id}'} ({chat.type.value})")
    
    @client.on("new_message")
    async def on_new_message(message):
        print(f"[{message.chat_title}] {message.sender_name}: {message.text}")
        
        if message.text.lower() == "hello":
            await message.reply("Hello! How are you?")
        
        if message.text.lower() == "test":
            chat = message.chat
            if chat:
                await chat.send_message("Test message")
        
        # Example: Send sticker on command
        if message.text.lower() == "sticker":
            await messaкакge.reply_sticker(80382389)  # Example sticker ID
    
    @client.on("contacts_update")
    async def on_contacts_update(contacts):
        print(f"Contacts updated: {len(contacts)}")
        for contact in contacts:
            if contact.name:
                print(f"  - {contact.name} (ID: {contact.id})")
    
    async def code_callback():
        return input("Enter confirmation code: ")
    
    phone_number = os.getenv("PHONE")
    if not phone_number:
        raise ValueError("PHONE environment variable is not set")
    
    await client.start(
        phone=phone_number, #number
        code_callback=code_callback
    )
    
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())