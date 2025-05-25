# Powered By Team DeadlineTech

import asyncio
from datetime import datetime, timedelta

from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import Message

import config
from DeadlineTech import app
from DeadlineTech.utils.database import get_client, is_active_chat
from DeadlineTech.misc import SUDOERS

AUTO_LEAVE_ENABLED = True

def seconds_until_4am():
    now = datetime.now()
    target = now.replace(hour=4, minute=0, second=0, microsecond=0)
    if now >= target:
        target += timedelta(days=1)
    return (target - now).total_seconds()

@app.on_message(filters.command("auto_leave") & SUDOERS)
async def toggle_auto_leave(_, message: Message):
    global AUTO_LEAVE_ENABLED
    AUTO_LEAVE_ENABLED = not AUTO_LEAVE_ENABLED
    state = "enabled" if AUTO_LEAVE_ENABLED else "disabled"
    await message.reply_text(f"✅ Auto Leave has been <b>{state}</b>.")

async def scheduled_auto_leave():
    from DeadlineTech.core.userbot import assistants
    while True:
        sleep_time = seconds_until_4am()
        await asyncio.sleep(sleep_time)
        
        if not AUTO_LEAVE_ENABLED:
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
                                    left += 1
                                except:
                                    continue
            except Exception as e:
                print(f"[AutoLeave Error] {e}")
                continue

# Start Task
asyncio.create_task(scheduled_auto_leave())
