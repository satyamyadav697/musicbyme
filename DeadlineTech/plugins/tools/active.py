from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from datetime import datetime
from zoneinfo import ZoneInfo

from DeadlineTech import app
from DeadlineTech.misc import SUDOERS
from DeadlineTech.utils.database import (
    get_active_chats,
    get_active_video_chats,
    remove_active_chat,
    remove_active_video_chat,
)

CALLS_CLOSE = "calls_close"
TIMEZONE = "Asia/Kolkata"


async def get_call_stats_detailed():
    voice_chats = []
    video_chats = []

    voice_ids = await get_active_chats()
    video_ids = await get_active_video_chats()

    for cid in voice_ids:
        try:
            chat = await app.get_chat(cid)
            voice_chats.append(f"• <b>{chat.title}</b> [<code>{cid}</code>]")
        except:
            await remove_active_chat(cid)

    for cid in video_ids:
        try:
            chat = await app.get_chat(cid)
            video_chats.append(f"• <b>{chat.title}</b> [<code>{cid}</code>]")
        except:
            await remove_active_video_chat(cid)

    return voice_chats, video_chats


def get_current_time():
    now = datetime.now(ZoneInfo(TIMEZONE))
    return now.strftime("%d %b %Y • %I:%M %p")


def generate_detailed_text(voice_list, video_list):
    voice_count = len(voice_list)
    video_count = len(video_list)
    total = voice_count + video_count

    text = (
        "📊 <b>Real-Time Call Activity</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔊 <b>Voice Chats:</b> <code>{voice_count}</code>\n"
    )

    if voice_list:
        text += "\n" + "\n".join(voice_list)

    text += (
        "\n━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎥 <b>Video Chats:</b> <code>{video_count}</code>\n"
    )

    if video_list:
        text += "\n" + "\n".join(video_list)

    text += (
        "\n━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📞 <b>Total Active Calls:</b> <code>{total}</code>\n"
        f"🕒 <b>Last Updated:</b> <code>{get_current_time()}</code>"
    )

    return text


def generate_minimal_text(voice_count, video_count):
    total = voice_count + video_count
    return (
        "📊 <b>Real-Time Call Activity</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔊 <b>Voice Chats:</b> <code>{voice_count}</code>\n"
        f"🎥 <b>Video Chats:</b> <code>{video_count}</code>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📞 <b>Total Active Calls:</b> <code>{total}</code>\n"
        f"🕒 <b>Last Updated:</b> <code>{get_current_time()}</code>"
    )


@app.on_message(filters.command(["activecalls", "acalls"]) & SUDOERS)
async def active_calls(_, message: Message):
    voice_list, video_list = await get_call_stats_detailed()
    detailed_text = generate_detailed_text(voice_list, video_list)

    button = InlineKeyboardMarkup(
        [[InlineKeyboardButton("✖ Close", callback_data=CALLS_CLOSE)]]
    )

    if len(detailed_text) > 2000:
        # If message too long, fallback to minimal version
        text = generate_minimal_text(len(voice_list), len(video_list))
    else:
        text = detailed_text

    await message.reply_text(text, reply_markup=button)


@app.on_callback_query(filters.regex(CALLS_CLOSE) & SUDOERS)
async def close_calls(_, query: CallbackQuery):
    await query.message.delete()
    await query.answer("closed❗")
