import asyncio
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import (
    ChatAdminRequired,
    InviteRequestSent,
    UserAlreadyParticipant,
    UserNotParticipant,
    ChatWriteForbidden,
)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from DeadlineTech import YouTube, app
from DeadlineTech.misc import SUDOERS
from DeadlineTech.utils.database import (
    get_assistant,
    get_cmode,
    get_lang,
    get_playmode,
    get_playtype,
    is_active_chat,
    is_maintenance,
)
from DeadlineTech.utils.inline import botplaylist_markup
from config import PLAYLIST_IMG_URL, SUPPORT_CHAT, adminlist
from strings import get_string

links = {}

def PlayWrapper(command):
    async def wrapper(client, message):
        language = await get_lang(message.chat.id)
        _ = get_string(language)

        # Handle anonymous admin messages
        if message.sender_chat:
            markup = InlineKeyboardMarkup(
                [[
                    InlineKeyboardButton("ʜᴏᴡ ᴛᴏ ғɪx ?", callback_data="AnonymousAdmin")
                ]]
            )
            try:
                return await message.reply_text(_["general_3"], reply_markup=markup)
            except ChatWriteForbidden:
                return await client.send_message(
                    message.from_user.id,
                    "❌ I can't send messages in this chat. Please allow me to write messages."
                )

        # Maintenance check
        if await is_maintenance():
            if message.from_user.id not in SUDOERS:
                try:
                    return await message.reply_text(
                        f"{app.mention} ɪs ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ. Visit <a href={SUPPORT_CHAT}>support chat</a> for more info.",
                        disable_web_page_preview=True
                    )
                except ChatWriteForbidden:
                    return await client.send_message(
                        message.from_user.id,
                        "❌ Bot is under maintenance and I can't send messages in the chat."
                    )

        try:
            await message.delete()
        except:
            pass

        # Get content sources
        audio = (message.reply_to_message.audio or message.reply_to_message.voice) if message.reply_to_message else None
        video = (message.reply_to_message.video or message.reply_to_message.document) if message.reply_to_message else None
        url = await YouTube.url(message)

        if not audio and not video and not url:
            if len(message.command) < 2:
                if "stream" in message.command:
                    try:
                        return await message.reply_text(_["str_1"])
                    except ChatWriteForbidden:
                        return await client.send_message(message.from_user.id, _["str_1"])
                buttons = botplaylist_markup(_)
                try:
                    return await message.reply_photo(
                        photo=PLAYLIST_IMG_URL,
                        caption=_["play_18"],
                        reply_markup=InlineKeyboardMarkup(buttons),
                    )
                except ChatWriteForbidden:
                    return await client.send_message(
                        message.from_user.id,
                        _["play_18"]
                    )

        # Channel play mode
        if message.command[0][0] == "c":
            chat_id = await get_cmode(message.chat.id)
            if not chat_id:
                try:
                    return await message.reply_text(_["setting_7"])
                except ChatWriteForbidden:
                    return await client.send_message(message.from_user.id, _["setting_7"])
            try:
                chat = await app.get_chat(chat_id)
                channel = chat.title
            except:
                return await message.reply_text(_["cplay_4"])
        else:
            chat_id = message.chat.id
            channel = None

        # Permission checks
        playmode = await get_playmode(message.chat.id)
        playty = await get_playtype(message.chat.id)
        if playty != "Everyone" and message.from_user.id not in SUDOERS:
            admins = adminlist.get(message.chat.id)
            if not admins:
                return await message.reply_text(_["admin_13"])
            if message.from_user.id not in admins:
                return await message.reply_text(_["play_4"])

        # Video and force play flags
        video = (
            True if message.command[0][0] == "v"
            else True if "-v" in message.text
            else True if message.command[0][1:2] == "v"
            else None
        )
        fplay = True if message.command[0][-1] == "e" else None

        # Ensure assistant joins if not active
        if not await is_active_chat(chat_id):
            userbot = await get_assistant(chat_id)
            try:
                member = await app.get_chat_member(chat_id, userbot.id)
                if member.status in [ChatMemberStatus.BANNED, ChatMemberStatus.RESTRICTED]:
                    return await message.reply_text(
                        _["call_2"].format(app.mention, userbot.id, userbot.name, userbot.username)
                    )
            except UserNotParticipant:
                if chat_id in links:
                    invitelink = links[chat_id]
                else:
                    if message.chat.username:
                        invitelink = message.chat.username
                        try:
                            await userbot.resolve_peer(invitelink)
                        except:
                            pass
                    else:
                        try:
                            invitelink = await app.export_chat_invite_link(chat_id)
                        except ChatAdminRequired:
                            try:
                                return await message.reply_text(_["call_1"])
                            except ChatWriteForbidden:
                                return await client.send_message(
                                    message.from_user.id,
                                    "❌ I can't send messages in this chat. Please give me permission to write."
                                )
                        except Exception as e:
                            return await message.reply_text(
                                _["call_3"].format(app.mention, type(e).__name__)
                            )

                if invitelink.startswith("https://t.me/+"):
                    invitelink = invitelink.replace("https://t.me/+", "https://t.me/joinchat/")

                try:
                    myu = await message.reply_text(_["call_4"].format(app.mention))
                except ChatWriteForbidden:
                    myu = await client.send_message(
                        message.from_user.id,
                        _["call_4"].format(app.mention)
                    )

                try:
                    await asyncio.sleep(1)
                    await userbot.join_chat(invitelink)
                except InviteRequestSent:
                    try:
                        await app.approve_chat_join_request(chat_id, userbot.id)
                        await asyncio.sleep(3)
                        await myu.edit(_["call_5"].format(app.mention))
                    except Exception as e:
                        return await message.reply_text(
                            _["call_3"].format(app.mention, type(e).__name__)
                        )
                except UserAlreadyParticipant:
                    pass
                except Exception as e:
                    return await message.reply_text(
                        _["call_3"].format(app.mention, type(e).__name__)
                    )

                links[chat_id] = invitelink

                try:
                    await userbot.resolve_peer(chat_id)
                except:
                    pass

        # Call actual command
        return await command(
            client,
            message,
            _,
            chat_id,
            video,
            channel,
            playmode,
            url,
            fplay,
        )

    return wrapper
