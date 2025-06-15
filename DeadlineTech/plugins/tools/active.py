# Powered By Team DeadlineTech

import logging
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from datetime import datetime
from zoneinfo import ZoneInfo

from DeadlineTech import app
from DeadlineTech.misc import SUDOERS
from DeadlineTech.utils.database import get_active_chats, get_active_video_chats

# Logger setup
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

CALLS_CLOSE = "calls_close"
TIMEZONE = "Asia/Kolkata"


def get_current_time():
    try:
        now = datetime.now(ZoneInfo(TIMEZONE))
        return now.strftime("%d %b %Y • %I:%M %p")
    except Exception as e:
        logger.exception(f"Error getting current time: {e}")
        return "Unknown Time"


def generate_summary_text(voice_count, video_count):
    total = voice_count + video_count
    return (
        "🔔 <b>Live Call Monitoring</b>\n"
        "<i>Tracking active media calls across chats</i>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎙️ <b>Voice Chats:</b> <code>{voice_count}</code>\n"
        f"📹 <b>Video Chats:</b> <code>{video_count}</code>\n"
        f"📊 <b>Total Active:</b> <code>{total}</code>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🕒 <b>Last Updated:</b> <code>{get_current_time()}</code>\n"
        "<b>Powered by</b> ⚡ <a href="https://t.me/DeadlineTechTeam">Team DeadlineTech</a>"
    )


@app.on_message(filters.command(["activecalls", "acalls"]) & SUDOERS)
async def active_calls(_, message: Message):
    try:
        voice_ids = await get_active_chats()
        video_ids = await get_active_video_chats()
    except Exception as e:
        logger.exception("Error fetching active chats or video chats.")
        return await message.reply_text("❌ Failed to fetch active calls. Check logs for details.")

    try:
        text = generate_summary_text(len(voice_ids), len(video_ids))
        button = InlineKeyboardMarkup(
            [[InlineKeyboardButton("❌ Close", callback_data=CALLS_CLOSE)]]
        )
        await message.reply_text(text, reply_markup=button)
    except Exception as e:
        logger.exception("Failed to send summary message.")
        await message.reply_text("❌ Error displaying call summary.")


@app.on_callback_query(filters.regex(CALLS_CLOSE) & SUDOERS)
async def close_calls(_, query: CallbackQuery):
    try:
        await query.message.delete()
        await query.answer("Closed!")
    except Exception as e:
        logger.exception("Failed to close the inline message.")
        try:
            await query.answer("❌ Couldn't close the message.", show_alert=True)
        except:
            pass
