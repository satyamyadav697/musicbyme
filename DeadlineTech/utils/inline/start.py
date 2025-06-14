from pyrogram.types import InlineKeyboardButton, WebAppInfo
import config
from DeadlineTech import app

def start_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text="➕ Add Me to Group",
                url=f"https://t.me/{app.username}?startgroup=true"
            ), 
            InlineKeyboardButton(text="💬 Support", url=config.SUPPORT_CHAT)
        ],
        [
            InlineKeyboardButton(
                text="💻 Source Code",
                url="https://github.com/DeadlineTech/music"
            )
        ]
    ]
    return buttons


def private_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text="➕ Add Me to Group",
                url=f"https://t.me/{app.username}?startgroup=true"
            )
        ],
        [
            InlineKeyboardButton(text="🆘 Help & Commands", callback_data="settings_back_helper")
        ],

        [
            InlineKeyboardButton(text="💬 Support", url=config.SUPPORT_CHAT),
            InlineKeyboardButton(text="📢 Updates", url=config.SUPPORT_CHANNEL)
        ],
        [
            InlineKeyboardButton(text="💻 Source Code", url="https://github.com/DeadlineTech/music")
        ]
    ]
    return buttons
