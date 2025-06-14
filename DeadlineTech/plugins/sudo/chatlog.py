# Powered By Team DeadlineTech

import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from DeadlineTech import app
from config import LOGGER_ID as JOINLOGS

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Cache the bot's ID at startup
BOT_ID = None


@app.on_message(filters.new_chat_members)
async def on_new_chat_members(client: Client, message: Message):
    global BOT_ID

    try:
        if BOT_ID is None:
            bot_user = await client.get_me()
            BOT_ID = bot_user.id
            logger.info(f"Cached bot ID: {BOT_ID}")
    except Exception as e:
        logger.exception("Failed to get bot info")
        return

    for new_member in message.new_chat_members:
        if new_member.id == BOT_ID:
            chat = message.chat
            chat_type = chat.type.name.capitalize()

            # Leave if added to a Channel (not supported)
            if chat_type == "Channel":
                try:
                    await client.leave_chat(chat.id)
                    logger.warning(f"Left channel: {chat.title} ({chat.id})")
                    return
                except Exception as e:
                    logger.exception(f"Failed to leave channel: {chat.title}")
                    return

            try:
                added_by = (
                    f"<a href='tg://user?id={message.from_user.id}'>👤 {message.from_user.first_name}</a>"
                    if message.from_user else "🕵️‍♂️ Unknown User"
                )

                chat_title = chat.title
                chat_id = chat.id
                chat_username = f"@{chat.username}" if chat.username else "🔒 Private Group"
                chat_link = f"https://t.me/{chat.username}" if chat.username else None

                # Get member count (best effort)
                try:
                    members_count = await client.get_chat_members_count(chat_id)
                except:
                    members_count = "N/A"

                log_text = (
                    "<b>🚀 Bot Added Successfully!</b>\n\n"
                    "╭───────⍟\n"
                    f"├ 💬 <b>Chat Name:</b> <code>{chat_title}</code>\n"
                    f"├ 🆔 <b>Chat ID:</b> <code>{chat_id}</code>\n"
                    f"├ 🧩 <b>Chat Type:</b> {chat_type}\n"
                    f"├ 👥 <b>Members:</b> <code>{members_count}</code>\n"
                    f"├ 🌐 <b>Username:</b> {chat_username}\n"
                    f"└ 👤 <b>Added By:</b> {added_by}\n"
                    "╰─────────────⍟"
                )

                buttons = [
                    [
                        InlineKeyboardButton("🌟 Visit Chat", url=chat_link)
                    ]
                ] if chat_link else None

                await client.send_message(
                    JOINLOGS,
                    text=log_text,
                    reply_markup=InlineKeyboardMarkup(buttons) if buttons else None,
                    disable_web_page_preview=True
                )
                logger.info(f"Join log sent for chat ID: {chat_id}")
            except Exception as e:
                logger.exception(f"[JOINLOG ERROR] Failed to send join log for chat ID: {chat.id}")
