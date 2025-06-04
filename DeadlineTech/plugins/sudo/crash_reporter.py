# Powered by DeadlineTech

from pyrogram import Client, filters
from pyrogram.types import Message
from DeadlineTech.utils.crash_reporter import sudo_alert_on_crash
from DeadlineTech import app


@app.on_message(filters.command("testcrash"))
@sudo_alert_on_crash
async def test_crash(_, message: Message):
    # Force a crash
    1 / 0  # This will raise ZeroDivisionError
