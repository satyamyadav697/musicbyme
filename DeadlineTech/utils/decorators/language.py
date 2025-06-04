from DeadlineTech.misc import SUDOERS
from DeadlineTech.utils.database import get_lang, is_maintenance
from strings import get_string
from config import SUPPORT_CHAT
from DeadlineTech import app


def languageCB(mystic):
    async def wrapper(_, CallbackQuery, **kwargs):
        try:
            # Check maintenance mode
            if await is_maintenance() is False:
                if CallbackQuery.from_user.id not in SUDOERS:
                    try:
                        await CallbackQuery.answer(
                            f"{app.mention} ɪs ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ.\nVisit {SUPPORT_CHAT} for more info.",
                            show_alert=True,
                        )
                    except Exception as e:
                        print(f"[languageCB] Callback answer failed: {e}")
                    return

            # Language detection
            try:
                language = await get_lang(CallbackQuery.message.chat.id)
                language = get_string(language)
            except Exception as e:
                print(f"[languageCB] Language fallback due to error: {e}")
                language = get_string("en")

            return await mystic(_, CallbackQuery, language)

        except Exception as err:
            print(f"[languageCB] Unexpected error: {err}")
            return

    return wrapper
