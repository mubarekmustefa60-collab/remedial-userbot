import os
import asyncio
from threading import Thread
from flask import Flask

# 1. Pyrogram Event Loop እንዲያገኝ ቀድመን Loop እንፈጥራለን
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

from pyrogram import Client, filters
from pyrogram.types import Message

# Flask ሰርቨር ለ Render ዌብ ሰርቪስ
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Remedial UserBot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)

# የቴሌግራም UserBot ማዋቀሪያ
API_ID = int(os.environ.get("API_ID", 1234567))
API_HASH = os.environ.get("API_HASH", "your_api_hash_here")
SESSION_STRING = os.environ.get("SESSION_STRING", "")

app = Client("remedial_bot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

@app.on_message(filters.text)
async def download_handler(client: Client, message: Message):
    text = message.text
    if "t.me/" in text:
        try:
            await message.reply("⏳ ፋይሉን በማውረድ ላይ ነው...")
            parts = text.split("/")
            msg_id = int(parts[-1])
            
            if "c" in parts:
                chat_id = int("-100" + parts[-1 - 1])
            else:
                chat_id = parts[-2]

            target_msg = await client.get_messages(chat_id, msg_id)
            
            if target_msg.video or target_msg.document or target_msg.audio:
                file_path = await target_msg.download()
                await client.send_document(
                    chat_id=message.chat.id,
                    document=file_path,
                    caption="✅ የተጠየቀው ማቴሪያል ተወርዷል!"
                )
                os.remove(file_path)
            else:
                await message.reply("⚠️ በዚህ ሊንክ ውስጥ ፋይል አልተገኘም!")
        except Exception as e:
            await message.reply(f"❌ ስህተት አጋጥሟል: {str(e)}")

async def start_services():
    # Flask Background Thread ሆኖ እንዲሰራ ማስጀመር
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    # Pyrogram Bot ማስጀመር
    await app.start()
    print("✅ ቦቱ በተሳካ ሁኔታ ስራ ጀምሯል!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    loop.run_until_complete(start_services())
