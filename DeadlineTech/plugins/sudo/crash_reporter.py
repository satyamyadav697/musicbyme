# Powered by DeadlineTech

from pyrogram import Client, filters
from DeadlineTech.utils.crash_reporter import sudo_alert_on_crash
from DeadlineTech import app
from pyrogram.types import Message, ChatMemberUpdated, DeletedMessages
from pyrogram.enums import ChatMemberStatus


@app.on_message(filters.command("testcrash"))
@sudo_alert_on_crash
async def test_crash(_, message: Message):
    # Force a crash
    1 / 0 



# ✅ Member joins, leaves, admin changes
@app.on_chat_member_updated()
async def handle_member_update(client: Client, update: ChatMemberUpdated):
    user = update.from_user
    chat = update.chat

    old = update.old_chat_member
    new = update.new_chat_member

    if old.status != new.status:
        if new.status == ChatMemberStatus.MEMBER:
            print(f"[JOIN] {user.first_name} ({user.id}) joined {chat.title} ({chat.id})")
        elif new.status == ChatMemberStatus.LEFT:
            print(f"[LEAVE] {user.first_name} ({user.id}) left {chat.title} ({chat.id})")
        elif new.status == ChatMemberStatus.ADMINISTRATOR:
            print(f"[PROMOTION] {user.first_name} ({user.id}) promoted in {chat.title} ({chat.id})")
        elif old.status == ChatMemberStatus.ADMINISTRATOR and new.status != ChatMemberStatus.ADMINISTRATOR:
            print(f"[DEMOTION] {user.first_name} ({user.id}) demoted in {chat.title} ({chat.id})")


# ✅ Voice chat started
@app.on_message(filters.voice_chat_started)
async def voice_chat_started_handler(client: Client, message: Message):
    chat = message.chat
    print(f"[VC STARTED] Voice Chat started in {chat.title} ({chat.id})")


# ✅ Voice chat ended
@app.on_message(filters.voice_chat_ended)
async def voice_chat_ended_handler(client: Client, message: Message):
    chat = message.chat
    print(f"[VC ENDED] Voice Chat ended in {chat.title} ({chat.id})")


# ✅ Message pinned
@app.on_message(filters.pinned_message)
async def pinned_message_handler(client: Client, message: Message):
    chat = message.chat
    print(f"[PINNED] Message pinned in {chat.title} ({chat.id}) - Msg ID: {message.message_id}")


# ✅ Message deleted
@app.on_deleted_messages()
async def deleted_message_handler(client: Client, deleted: DeletedMessages):
    chat = deleted.chat
    for msg in deleted.messages:
        print(f"[DELETED] A message was deleted in {chat.title} ({chat.id}) - Msg ID: {msg.id}")
