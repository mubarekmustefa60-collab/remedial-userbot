import os
import asyncio
from threading import Thread
from flask import Flask
from telethon import TelegramClient, events
from telethon.sessions import StringSession

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

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

@client.on(events.NewMessage)
async def download_handler(event):
    text = event.raw_text
    if "t.me/" in text:
        try:
            status_msg = await event.reply("⏳ ፋይሉን በማውረድ ላይ ነው...")
            parts = text.split("/")
            msg_id = int(parts[-1])
            
            if "c" in parts:
                chat_id = int("-100" + parts[-2])
            else:
                chat_id = parts[-2]

            target_msg = await client.get_messages(chat_id, ids=msg_id)
            
            if target_msg and target_msg.media:
                file_path = await target_msg.download_media()
                await client.send_file(
                    event.chat_id,
                    file_path,
                    caption="✅ የተጠየቀው ማቴሪያል ተወርዷል!"
                )
                os.remove(file_path)
                await status_msg.delete()
            else:
                await status_msg.edit("⚠️ በዚህ ሊንክ ውስጥ ፋይል አልተገኘም!")
        except Exception as e:
            await event.reply(f"❌ ስህተት አጋጥሟል: {str(e)}")

async def main():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    await client.start()
    print("✅ ቦቱ በተሳካ ሁኔታ ስራ ጀምሯል!")
    await client.run_until_disconnected()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
