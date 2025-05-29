# Powered by DeadlineTech

import asyncio
from datetime import datetime, timedelta

from pyrogram.enums import ChatType

import config
from DeadlineTech import app
from DeadlineTech.utils.database import get_client, is_active_chat

# Enable or disable auto leave
AUTO_LEAVE_ENABLED = True

# Calculate seconds until next 4 AM
def seconds_until_4am():
    now = datetime.now()
    target = now.replace(hour=4, minute=0, second=0, microsecond=0)
    if now >= target:
        target += timedelta(days=1)
    return (target - now).total_seconds()

# Command to toggle auto-leave (optional)
from pyrogram import filters
from pyrogram.types import Message
from DeadlineTech.misc import SUDOERS

@app.on_message(filters.command("auto_leave") & SUDOERS)
async def toggle_auto_leave(_, message: Message):
    global AUTO_LEAVE_ENABLED
    AUTO_LEAVE_ENABLED = not AUTO_LEAVE_ENABLED
    state = "enabled" if AUTO_LEAVE_ENABLED else "disabled"
    await message.reply_text(f"✅ Auto Leave has been <b>{state}</b>.")

# Main scheduled task
async def scheduled_auto_leave():
    from DeadlineTech.core.userbot import assistants

    print("[AutoLeave] Background task started.")
    while True:
        sleep_time = seconds_until_4am()
        print(f"[AutoLeave] Sleeping for {sleep_time} seconds until 4 AM.")
        await asyncio.sleep(sleep_time)

        if not AUTO_LEAVE_ENABLED:
            print("[AutoLeave] Skipped — feature disabled.")
            continue

        for num in assistants:
            client = await get_client(num)
            left = 0
            try:
                async for dialog in client.get_dialogs():
                    chat = dialog.chat
                    if chat.type in [ChatType.SUPERGROUP, ChatType.GROUP, ChatType.CHANNEL]:
                        if chat.id not in [config.LOGGER_ID, -1001686672798, -1001549206010]:
                            if left >= 20:
                                break
                            if not await is_active_chat(chat.id):
                                try:
                                    await client.leave_chat(chat.id)
                                    print(f"[AutoLeave] {client.me.first_name} left: {chat.title} ({chat.id})")
                                    left += 1
                                except Exception as e:
                                    print(f"[AutoLeave Error] Could not leave {chat.id}: {e}")
            except Exception as e:
                print(f"[AutoLeave Error] Assistant {num} failed: {e}")



