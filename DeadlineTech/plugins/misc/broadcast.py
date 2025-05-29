# Powered By Team DeadlineTech

import time
import asyncio

from pyrogram import filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.errors import FloodWait, RPCError

from DeadlineTech import app
from DeadlineTech.misc import SUDOERS
from DeadlineTech.utils.database import (
    get_active_chats,
    get_authuser_names,
    get_client,
    get_served_chats,
    get_served_users,
)
from DeadlineTech.utils.decorators.language import language
from DeadlineTech.utils.formatters import alpha_to_int
from config import adminlist

# Constants
BATCH_SIZE = 50
DELAY_BETWEEN_TASKS = 0.5
DELAY_BETWEEN_BATCHES = 2
MAX_RETRIES = 3

@app.on_message(filters.command("broadcast") & SUDOERS)
@language
async def broadcast_command(client, message, _):
    command_text = message.text.lower()
    mode = "forward" if "-forward" in command_text else "copy"

    # Target group parsing
    if "-all" in command_text:
        users = await get_served_users()
        chats = await get_served_chats()
        target_users = [doc["user_id"] for doc in users]
        target_chats = [doc["chat_id"] for doc in chats]
    elif "-users" in command_text:
        users = await get_served_users()
        target_users = [doc["user_id"] for doc in users]
        target_chats = []
    elif "-chats" in command_text:
        chats = await get_served_chats()
        target_chats = [doc["chat_id"] for doc in chats]
        target_users = []
    else:
        return await message.reply_text(
            "❗ <b>Invalid Usage</b>\n\n"
            "Please specify a valid target tag:\n"
            "<code>-all</code> → All users & chats\n"
            "<code>-users</code> → All users only\n"
            "<code>-chats</code> → All group chats only"
        )

    if not target_users and not target_chats:
        return await message.reply_text("⚠️ No valid targets found for broadcast.")

    # Message content
    if message.reply_to_message:
        content = message.reply_to_message
    else:
        raw = message.text
        for tag in ["-all", "-users", "-chats", "-forward"]:
            raw = raw.replace(tag, "")
        raw = raw.replace("/broadcast", "").strip()

        if not raw:
            return await message.reply_text(
                "📝 Please provide a message to broadcast or reply to one."
            )
        content = raw

    total_targets = len(target_users) + len(target_chats)
    sent_count = failed_count = 0
    sent_to_users = sent_to_chats = 0

    status_msg = await message.reply_text(
        f"📡 <b>Broadcast Started</b>\n"
        f"Mode: <code>{mode}</code>\n\n"
        f"Progress: <code>0%</code> ⏳"
    )

    start_time = time.time()

    async def send_message(chat_id):
        nonlocal sent_count, failed_count, sent_to_users, sent_to_chats

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                if isinstance(content, str):
                    await app.send_message(chat_id, content)
                elif mode == "forward":
                    await app.forward_messages(
                        chat_id=chat_id,
                        from_chat_id=message.chat.id,
                        message_ids=content.id
                    )
                else:
                    await content.copy(chat_id)

                sent_count += 1
                if chat_id in target_users:
                    sent_to_users += 1
                else:
                    sent_to_chats += 1
                return

            except FloodWait as e:
                logging.warning(f"FloodWait for {e.value}s on chat {chat_id}")
                await asyncio.sleep(e.value)
            except RPCError as e:
                logging.error(f"RPCError on chat {chat_id}: {e}")
                await asyncio.sleep(1)
            except Exception as e:
                logging.exception(f"Unexpected error on chat {chat_id}: {e}")
                await asyncio.sleep(1)

        failed_count += 1

    async def broadcast_batch(targets):
        nonlocal sent_count, failed_count

        for i in range(0, len(targets), BATCH_SIZE):
            batch = targets[i:i + BATCH_SIZE]

            for chat_id in batch:
                await send_message(chat_id)
                await asyncio.sleep(DELAY_BETWEEN_TASKS)

            percent = round((sent_count + failed_count) / total_targets * 100, 2)
            elapsed = time.time() - start_time
            eta = (elapsed / max(sent_count + failed_count, 1)) * (total_targets - (sent_count + failed_count))
            eta_formatted = f"{int(eta // 60)}m {int(eta % 60)}s"

            progress_bar = f"[{'█' * int(percent // 5)}{'░' * (20 - int(percent // 5))}]"

            await status_msg.edit_text(
                f"<b>📣 Broadcast In Progress</b>\n"
                f"{progress_bar} <code>{percent}%</code>\n\n"
                f"✅ Delivered: <code>{sent_count}</code>\n"
                f"❌ Failed: <code>{failed_count}</code>\n"
                f"⏱ Estimated Time Left: <code>{eta_formatted}</code>"
            )

            await asyncio.sleep(DELAY_BETWEEN_BATCHES)

    targets = target_users + target_chats
    await broadcast_batch(targets)

    total_time = round(time.time() - start_time, 2)
    await status_msg.edit_text(
        f"✅ <b>Broadcast Complete!</b>\n\n"
        f"🔘 Mode: <code>{mode}</code>\n"
        f"🎯 Total Targets: <code>{total_targets}</code>\n"
        f"📬 Successful Deliveries: <code>{sent_count}</code>\n"
        f"    ├ Users: <code>{sent_to_users}</code>\n"
        f"    └ Chats: <code>{sent_to_chats}</code>\n"
        f"❌ Failed Attempts: <code>{failed_count}</code>\n"
        f"⏰ Time Elapsed: <code>{total_time}s</code>"
    )


async def auto_clean():
    while not await asyncio.sleep(10):
        try:
            served_chats = await get_active_chats()
            for chat_id in served_chats:
                if chat_id not in adminlist:
                    adminlist[chat_id] = []
                    async for user in app.get_chat_members(
                        chat_id, filter=ChatMembersFilter.ADMINISTRATORS
                    ):
                        if user.privileges.can_manage_video_chats:
                            adminlist[chat_id].append(user.user.id)
                    authusers = await get_authuser_names(chat_id)
                    for user in authusers:
                        user_id = await alpha_to_int(user)
                        adminlist[chat_id].append(user_id)
        except:
            continue


asyncio.create_task(auto_clean())
