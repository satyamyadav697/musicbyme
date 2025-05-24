from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from datetime import datetime

from DeadlineTech import app
from DeadlineTech.misc import SUDOERS
from DeadlineTech.utils.database import (
    get_active_chats,
    get_active_video_chats,
    remove_active_chat,
    remove_active_video_chat,
)

CALLS_REFRESH = "calls_refresh"


async def get_call_stats():
    voice = await get_active_chats()
    video = await get_active_video_chats()

    # Cleanup invalid chats
    for cid in voice:
        try:
            await app.get_chat(cid)
        except:
            await remove_active_chat(cid)

    for cid in video:
        try:
            await app.get_chat(cid)
        except:
            await remove_active_video_chat(cid)

    return len(voice), len(video)


def get_current_time():
    return datetime.now().strftime("%d %b %Y • %I:%M %p")


@app.on_message(filters.command(["activecalls", "acalls"]) & SUDOERS)
async def active_calls(_, message: Message):
    voice_count, video_count = await get_call_stats()
    total = voice_count + video_count

    text = (
        "🎧 <b>Active Call Stats</b>\n\n"
        f"🔊 Voice Chats : <code>{voice_count}</code>\n"
        f"🎥 Video Chats : <code>{video_count}</code>\n"
        f"📞 Total Calls : <code>{total}</code>\n\n"
        f"🕒 <i>Updated on:</i> <code>{get_current_time()}</code>"
    )

    button = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔄 Refresh", callback_data=CALLS_REFRESH)]]
    )

    await message.reply_text(text, reply_markup=button)


@app.on_callback_query(filters.regex(CALLS_REFRESH) & SUDOERS)
async def refresh_calls(_, query: CallbackQuery):
    voice_count, video_count = await get_call_stats()
    total = voice_count + video_count

    text = (
        "🎧 <b>Active Call Stats</b>\n\n"
        f"🔊 Voice Chats : <code>{voice_count}</code>\n"
        f"🎥 Video Chats : <code>{video_count}</code>\n"
        f"📞 Total Calls : <code>{total}</code>\n\n"
        f"🕒 <i>Updated on:</i> <code>{get_current_time()}</code>"
    )

    await query.message.edit_text(text, reply_markup=query.message.reply_markup)
    await query.answer("Updated!")
