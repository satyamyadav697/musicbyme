# 🎿 DeadlineTech Music Bot (Powered by Team DeadlineTech)

import os
import re
import asyncio
import requests
import logging
import urllib.request
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ChatAction
from youtubesearchpython.__future__ import VideosSearch
from config import API_KEY, API_BASE_URL
from DeadlineTech import app

# 📝 Logging Setup
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    handlers=[
        logging.FileHandler("logs/music_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

MIN_FILE_SIZE = 51200
DOWNLOADS_DIR = "downloads"
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

# 🔍 Extract YouTube video ID
def extract_video_id(link: str) -> str | None:
    patterns = [
        r'youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=)([0-9A-Za-z_-]{11})',
        r'youtu\.be\/([0-9A-Za-z_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, link)
        if match:
            return match.group(1)
    return None

# 📸 Download thumbnail
def download_thumbnail(video_id: str) -> str | None:
    try:
        url = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
        path = os.path.join(DOWNLOADS_DIR, f"{video_id}.jpg")
        urllib.request.urlretrieve(url, path)
        return path
    except Exception as e:
        logger.warning(f"Thumbnail error: {e}")
        return None

# 🔽 API Downloader
def api_dl(video_id: str) -> str | None:
    try:
        url = f"{API_BASE_URL}/download/song/{video_id}?key={API_KEY}"
        file_path = os.path.join(DOWNLOADS_DIR, f"{video_id}.mp3")
        if os.path.exists(file_path):
            return file_path
        response = requests.get(url, stream=True, timeout=15)
        if response.status_code == 200:
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            if os.path.getsize(file_path) < MIN_FILE_SIZE:
                os.remove(file_path)
                return None
            return file_path
    except Exception as e:
        logger.error(f"Download failed: {e}")
    return None

# ⏳ Delayed cleanup
async def remove_file_later(path: str, delay: int = 600):
    await asyncio.sleep(delay)
    if os.path.exists(path):
        os.remove(path)
        logger.info(f"Deleted: {path}")

def parse_duration(duration: str) -> int:
    parts = list(map(int, duration.split(":")))
    if len(parts) == 3:
        h, m, s = parts
    elif len(parts) == 2:
        h, m = 0, parts[0]
        s = parts[1]
    else:
        return int(parts[0])
    return h * 3600 + m * 60 + s

# 🎵 Command Handler
@app.on_message(filters.command(["song", "music"]))
async def song_command(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(
            "🎶 <b>Usage:</b>\nSend <code>/music [song name or YouTube link]</code> to get a track!"
        )

    query = message.text.split(None, 1)[1].strip()
    video_id = extract_video_id(query)

    if video_id:
        await message.reply_text("🎼 <i>Fetching your track...</i>")
        await send_audio(client, message, video_id)
    else:
        await message.reply_text("🔍 <i>Searching YouTube...</i>")
        try:
            results = (await VideosSearch(query, limit=5).next()).get('result', [])
            if not results:
                return await message.reply_text("❌ <b>No songs found.</b> Try something else.")
            buttons = [[
                InlineKeyboardButton(f"🎵 {video['title'][:30]}{'...' if len(video['title']) > 30 else ''}",
                                     callback_data=f"dl_{video['id']}")
            ] for video in results]
            await message.reply_text(
                "🎧 <b>Choose your song:</b>",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        except Exception as e:
            logger.error(f"Search error: {e}")
            await message.reply_text("⚠️ <b>Error while searching.</b> Try again later.")

# 🔘 Callback for selected song
@app.on_callback_query(filters.regex(r"^dl_(.+)$"))
async def callback_handler(client: Client, cq: CallbackQuery):
    video_id = cq.data.split("_", 1)[1]
    await cq.answer("🎶 Downloading...")
    await cq.message.edit("⏳ <i>Processing your track...</i>")
    await send_audio(client, cq.message, video_id)
    await cq.message.edit("✅ <b>Done!</b> Use /music to get more songs 🎵")

# 📤 Send Audio Function
async def send_audio(client: Client, message: Message, video_id: str):
    try:
        result = (await VideosSearch(video_id, limit=1).next())["result"][0]
        title = result.get("title", "Unknown")
        duration_str = result.get("duration", "0:00")
        duration = parse_duration(duration_str)
        url = result.get("link")
    except Exception as e:
        logger.warning(f"Metadata error: {e}")
        title, duration_str, duration, url = "Unknown", "0:00", 0, None

    thumb_path = await asyncio.to_thread(download_thumbnail, video_id)
    file_path = await asyncio.to_thread(api_dl, video_id)

    if not file_path:
        return await message.reply_text("❌ <b>Couldn’t download the song.</b> Try a different one.")

    audio_msg = await message.reply_audio(
        audio=file_path,
        title=title,
        performer="DeadlineTech",
        duration=duration,
        caption=f"🎿 <b>{title}</b>\n🕒 <b>Duration:</b> {duration_str}\n🔗 <a href=\"{url}\">YouTube</a>\n\n🔧 <b>Powered by:</b> <a href=\"https://t.me/DeadlineTechTeam\">Team DeadlineTech</a>\n🤝 <i>Want to contribute?</i> Check our bot repo!",
        thumb=thumb_path if thumb_path else None,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🎧 More Music", url="https://t.me/DeadlineTechMusic")],
            [InlineKeyboardButton("💻 Contribute", url="https://github.com/DeadlineTech/music")]  
        ])
    )

    if thumb_path:
        asyncio.create_task(remove_file_later(thumb_path))
    asyncio.create_task(remove_file_later(file_path))
