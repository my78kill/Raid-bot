import asyncio
import json
import os
import random
import time
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from telegram.constants import ParseMode, ChatType
from telegram.error import TelegramError, RetryAfter
import logging
from typing import Dict, Optional, Set, List
import threading
from flask import Flask
app = Flask(__name__)

# ===================== CONFIGURATION =====================
BOT_TOKEN = '8785963267:AAGVuuqKNPb90TnRABoi6kLCVCnjqXQq2hM'

application = Application.builder().token(BOT_TOKEN).build()

OWNER_ID = (8539769704,
            7512786892)  # You can add multiple owner IDs as a tuple
ACCESS_CODE = 'adam412tttyu'

# FLOOD-FREE SETTINGS
MAX_MESSAGES_PER_SECOND = 30
MAX_MESSAGES_PER_MINUTE = 180
MESSAGE_DELAY = 0.035
STICKER_DELAY = 0.05
MAX_RAID_COUNT = 200
MAX_SPAM_COUNT = 150
MAX_STICKER_COUNT = 100

# Files
USERS_FILE = 'authorized_users.json'
GROUPS_FILE = 'authorized_groups.json'
MUTED_USERS_FILE = 'muted_users.json'
RAID_HISTORY_FILE = 'raid_history.json'
STICKERS_FILE = 'saved_stickers.json'  # New file for saved stickers

# ===================== RAID MESSAGES =====================
RAID_MESSAGES = [
    "𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗜 𝗖𝗛𝗨𝗧 𝗠𝗘 𝗖𝗛𝗔𝗞𝗨 𝗗𝗔𝗔𝗟 𝗞𝗔𝗥 𝗖𝗛𝗨𝗧 𝗞𝗔 𝗞𝗛𝗢𝗢𝗡 𝗞𝗔𝗥 𝗗𝗨𝗡𝗚𝗔",
    "𝗧𝗘𝗥𝗜 𝗕𝗘𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗧 𝗠𝗘 𝗞𝗘𝗟𝗘 𝗞𝗘 𝗖𝗛𝗜𝗟𝗞𝗘",
    "𝗧𝗘𝗥𝗜 𝗕𝗘𝗛𝗘𝗡 𝗟𝗘𝗧𝗜 𝗠𝗘𝗥𝗜 𝗟𝗨𝗡𝗗 𝗕𝗔𝗗𝗘 𝗠𝗔𝗦𝗧𝗜 𝗦𝗘",
    "𝗧𝗘𝗥𝗜 𝗕𝗘𝗛𝗘𝗡 𝗞𝗢 𝗠𝗘𝗡𝗘 𝗖𝗛𝗢𝗗 𝗗𝗔𝗟𝗔 𝗕𝗢𝗛𝗢𝗧 𝗦𝗔𝗦𝗧𝗘 𝗦𝗘",
    "𝗧𝗘𝗥𝗘 𝗕𝗔𝗔𝗣 𝗞𝗔 𝗕𝗛𝗢𝗦𝗗𝗔 𝗠𝗔𝗗𝗔𝗥𝗖𝗛𝗢𝗗",
    "𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗢 𝗟𝗘𝗞𝗘 𝗕𝗛𝗔𝗚 𝗝𝗔𝗔𝗨𝗡𝗚𝗔",
    "𝗞𝗜𝗗𝗭 𝗠𝗔𝗗𝗔𝗥𝗖𝗛𝗢𝗗 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗢 𝗖𝗛𝗢𝗗 𝗖𝗛𝗢𝗗𝗞𝗘",
    "𝗝𝗨𝗡𝗚𝗟𝗘 𝗠𝗘 𝗡𝗔𝗖𝗛𝗧𝗔 𝗛𝗘 𝗠𝗢𝗥𝗘 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗜 𝗖𝗛𝗨𝗗𝗔𝗜",
    "𝗚𝗔𝗟𝗜 𝗚𝗔𝗟𝗜 𝗠𝗘 𝗥𝗘𝗛𝗧𝗔 𝗛𝗘 𝗦𝗔𝗡𝗗 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗢 𝗖𝗛𝗢𝗗 𝗗𝗔𝗟𝗔",
    "𝗦𝗔𝗕 𝗕𝗢𝗟𝗧𝗘 𝗠𝗨𝗝𝗛𝗞𝗢 𝗣𝗔𝗣𝗔 𝗞𝗬𝗢𝗨𝗡𝗞𝗜 𝗠𝗘𝗡𝗘 𝗕𝗔𝗡𝗔𝗗𝗜𝗔 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗢 𝗣𝗥𝗘𝗚𝗡𝗘𝗡𝗧",
    "𝗧𝗘𝗥𝗜 𝗕𝗘‌𝗛𝗘𝗡 𝗞𝗢𝗧𝗢 𝗖𝗛𝗢𝗗 𝗖𝗛𝗢𝗗𝗞𝗘 𝗣𝗨𝗥𝗔 𝗙𝗔𝗔𝗗 𝗗𝗜𝗔 𝗖𝗛𝗨𝗨‌𝗧𝗛 𝗔𝗕𝗕 𝗧𝗘𝗥𝗜 𝗚𝗙 𝗞𝗢 𝗕𝗛𝗘𝗝 😆💦🤤",
    "𝗧𝗘𝗥𝗜 𝗚𝗙 𝗞𝗢 𝗘𝗧𝗡𝗔 𝗖𝗛𝗢𝗗𝗔 𝗕𝗘‌𝗛𝗘𝗡 𝗞𝗘 𝗟𝗢𝗗𝗘 𝗧𝗘𝗥𝗜 𝗚𝗙 𝗧𝗢 𝗠𝗘𝗥𝗜 𝗥Æ𝗡𝗗𝗜 𝗕𝗔𝗡𝗚𝗔𝗬𝗜 𝗔𝗕𝗕 𝗖𝗛𝗔𝗟 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗞𝗢 𝗖𝗛𝗢𝗗𝗧𝗔 𝗙𝗜𝗥𝗦𝗘 ♥️💦😆😆😆😆",
    "𝗛𝗔𝗥𝗜 𝗛𝗔𝗥𝗜 𝗚𝗛𝗔𝗔𝗦 𝗠𝗘 𝗝𝗛𝗢𝗣𝗗𝗔 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗞𝗔 𝗕𝗛𝗢𝗦𝗗𝗔 🤣🤣💋💦",
    "𝗖𝗛𝗔𝗟 𝗧𝗘𝗥𝗘 𝗕𝗔𝗔𝗣 𝗞𝗢 𝗕𝗛𝗘𝗝 𝗧𝗘𝗥𝗔 𝗕𝗔𝗦𝗞𝗔 𝗡𝗛𝗜 𝗛𝗘 𝗣𝗔𝗣𝗔 𝗦𝗘 𝗟𝗔𝗗𝗘𝗚𝗔 𝗧𝗨",
    "𝗧𝗘𝗥𝗜 𝗕𝗘‌𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧𝗛 𝗠𝗘 𝗕𝗢𝗠𝗕 𝗗𝗔𝗟𝗞𝗘 𝗨𝗗𝗔 𝗗𝗨𝗡𝗚𝗔 𝗠𝗔‌𝗔‌𝗞𝗘 𝗟𝗔𝗪𝗗𝗘",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗞𝗢 𝗧𝗥𝗔𝗜𝗡 𝗠𝗘 𝗟𝗘𝗝𝗔𝗞𝗘 𝗧𝗢𝗣 𝗕𝗘𝗗 𝗣𝗘 𝗟𝗜𝗧𝗔𝗞𝗘 𝗖𝗛𝗢𝗗 𝗗𝗨𝗡𝗚𝗔 𝗦𝗨𝗔𝗥 𝗞𝗘 𝗣𝗜𝗟𝗟𝗘 🤣🤣💋💋",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗔𝗞𝗘 𝗡𝗨𝗗𝗘𝗦 𝗚𝗢𝗢𝗚𝗟𝗘 𝗣𝗘 𝗨𝗣𝗟𝗢𝗔𝗗 𝗞𝗔𝗥𝗗𝗨𝗡𝗚𝗔 𝗕𝗘‌𝗛𝗘𝗡 𝗞𝗘 𝗟𝗔𝗘𝗪𝗗𝗘 👻🔥",
    "𝗧𝗘𝗥𝗜 𝗕𝗘‌𝗛𝗘𝗡 𝗞𝗢 𝗖𝗛𝗢𝗗 𝗖𝗛𝗢𝗗𝗞𝗘 𝗩𝗜𝗗𝗘𝗢 𝗕𝗔𝗡𝗔𝗞𝗘 𝗫𝗡𝗫𝗫.𝗖𝗢𝗠 𝗣𝗘 𝗡𝗘𝗘𝗟𝗔𝗠 𝗞𝗔𝗥𝗗𝗨𝗡𝗚𝗔 𝗞𝗨𝗧𝗧𝗘 𝗞𝗘 𝗣𝗜𝗟𝗟𝗘 💦💋",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗔𝗞𝗜 𝗖𝗛𝗨𝗗𝗔𝗜 𝗞𝗢 𝗣𝗢𝗥𝗡𝗛𝗨𝗕.𝗖𝗢𝗠 𝗣𝗘 𝗨𝗣𝗟𝗢𝗔𝗗 𝗞𝗔𝗥𝗗𝗨𝗡𝗚𝗔 𝗦𝗨𝗔𝗥 𝗞𝗘 𝗖𝗛𝗢𝗗𝗘 🤣💋💦",
    "𝗔𝗕𝗘 𝗧𝗘𝗥𝗜 𝗕𝗘‌𝗛𝗘𝗡 𝗞𝗢 𝗖𝗛𝗢𝗗𝗨 𝗥Æ𝗡𝗗𝗜𝗞𝗘 𝗕𝗔𝗖𝗛𝗛𝗘 𝗧𝗘𝗥𝗘𝗞𝗢 𝗖𝗛𝗔𝗞𝗞𝗢 𝗦𝗘 𝗣𝗜𝗟𝗪𝗔𝗩𝗨𝗡𝗚𝗔 𝗥Æ𝗡𝗗𝗜𝗞𝗘 𝗕𝗔𝗖𝗛𝗛𝗘 🤣🤣",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧𝗛 𝗙𝗔𝗔𝗗𝗞𝗘 𝗥𝗔𝗞𝗗𝗜𝗔 𝗠𝗔‌𝗔‌𝗞𝗘 𝗟𝗢𝗗𝗘 𝗝𝗔𝗔 𝗔𝗕𝗕 𝗦𝗜𝗟𝗪𝗔𝗟𝗘 👄👄",
    "𝗧𝗘𝗥𝗜 𝗕𝗘‌𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧𝗛 𝗠𝗘 𝗠𝗘𝗥𝗔 𝗟𝗨𝗡𝗗 𝗞𝗔𝗔𝗟𝗔",
    "𝗧𝗘𝗥𝗜 𝗕𝗘‌𝗛𝗘𝗡 𝗟𝗘𝗧𝗜 𝗠𝗘𝗥𝗜 𝗟𝗨𝗡𝗗 𝗕𝗔𝗗𝗘 𝗠𝗔𝗦𝗧𝗜 𝗦𝗘 𝗧𝗘𝗥𝗜 𝗕𝗘‌𝗛𝗘𝗡 𝗞𝗢 𝗠𝗘𝗡𝗘 𝗖𝗛𝗢𝗗 𝗗𝗔𝗟𝗔 𝗕𝗢𝗛𝗢𝗧 𝗦𝗔𝗦𝗧𝗘 𝗦𝗘",
    "𝗕𝗘𝗧𝗘 𝗧𝗨 𝗕𝗔𝗔𝗣 𝗦𝗘 𝗟𝗘𝗚𝗔 𝗣𝗔𝗡𝗚𝗔 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗔 𝗞𝗢 𝗖𝗛𝗢𝗗 𝗗𝗨𝗡𝗚𝗔 𝗞𝗔𝗥𝗞𝗘 𝗡𝗔𝗡𝗚𝗔 💦💋",
    "𝗛𝗔𝗛𝗔𝗛𝗔𝗛 𝗠𝗘𝗥𝗘 𝗕𝗘𝗧𝗘 𝗔𝗚𝗟𝗜 𝗕𝗔𝗔𝗥 𝗔𝗣𝗡𝗜 𝗠𝗔‌𝗔‌𝗞𝗢 𝗟𝗘𝗞𝗘 𝗔𝗔𝗬𝗔 𝗠𝗔𝗧𝗛 𝗞𝗔𝗧 𝗢𝗥 𝗠𝗘𝗥𝗘 𝗠𝗢𝗧𝗘 𝗟𝗨𝗡𝗗 𝗦𝗘 𝗖𝗛𝗨𝗗𝗪𝗔𝗬𝗔 𝗠𝗔𝗧𝗛 𝗞𝗔𝗥",
    "𝗖𝗛𝗔𝗟 𝗕𝗘𝗧𝗔 𝗧𝗨𝗝𝗛𝗘 𝗠𝗔‌𝗔‌𝗙 𝗞𝗜𝗔 🤣 𝗔𝗕𝗕 𝗔𝗣𝗡𝗜 𝗚𝗙 𝗞𝗢 𝗕𝗛𝗘𝗝",
    "𝗦𝗛𝗔𝗥𝗔𝗠 𝗞𝗔𝗥 𝗧𝗘𝗥𝗜 𝗕𝗘‌𝗛𝗘𝗡 𝗞𝗔 𝗕𝗛𝗢𝗦𝗗𝗔 𝗞𝗜𝗧𝗡𝗔 𝗚𝗔𝗔𝗟𝗜𝗔 𝗦𝗨𝗡𝗪𝗔𝗬𝗘𝗚𝗔 𝗔𝗣𝗡𝗜 𝗠𝗔‌𝗔‌𝗔 𝗕𝗘‌𝗛𝗘𝗡 𝗞𝗘 𝗨𝗣𝗘𝗥",
    "𝗔𝗕𝗘 𝗥Æ𝗡𝗗𝗜𝗞𝗘 𝗕𝗔𝗖𝗛𝗛𝗘 𝗔𝗨𝗞𝗔𝗧 𝗡𝗛𝗜 𝗛𝗘𝗧𝗢 𝗔𝗣𝗡𝗜 𝗥Æ𝗡𝗗𝗜 𝗠𝗔‌𝗔‌𝗞𝗢 𝗟𝗘𝗞𝗘 𝗔𝗔𝗬𝗔 𝗠𝗔𝗧𝗛 𝗞𝗔𝗥 𝗛𝗔𝗛𝗔𝗛𝗔𝗛𝗔",
    "𝗞𝗜𝗗𝗭 𝗠𝗔‌𝗔‌𝗗𝗔𝗥𝗖𝗛Ø𝗗 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗞𝗢 𝗖𝗛𝗢𝗗 𝗖𝗛𝗢𝗗𝗞𝗘 𝗧𝗘𝗥𝗥 𝗟𝗜𝗬𝗘 𝗕𝗛𝗔𝗜 𝗗𝗘𝗗𝗜𝗬𝗔",
    "𝗝𝗨𝗡𝗚𝗟𝗘 𝗠𝗘 𝗡𝗔𝗖𝗛𝗧𝗔 𝗛𝗘 𝗠𝗢𝗥𝗘 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗞𝗜 𝗖𝗛𝗨𝗗𝗔𝗜 𝗗𝗘𝗞𝗞𝗘 𝗦𝗔𝗕 𝗕𝗢𝗟𝗧𝗘 𝗢𝗡𝗖𝗘 𝗠𝗢𝗥𝗘 𝗢𝗡𝗖𝗘 𝗠𝗢𝗥𝗘 🤣🤣💦💋",
    "𝗚𝗔𝗟𝗜 𝗚𝗔𝗟𝗜 𝗠𝗘 𝗥𝗘𝗛𝗧𝗔 𝗛𝗘 𝗦𝗔𝗡𝗗 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗞𝗢 𝗖𝗛𝗢𝗗 𝗗𝗔𝗟𝗔 𝗢𝗥 𝗕𝗔𝗡𝗔 𝗗𝗜𝗔 𝗥𝗔𝗡𝗗 🤤🤣",
    "𝗦𝗔𝗕 𝗕𝗢𝗟𝗧𝗘 𝗠𝗨𝗝𝗛𝗞𝗢 𝗣𝗔𝗣𝗔 𝗞𝗬𝗢𝗨𝗡𝗞𝗜 𝗠𝗘𝗡𝗘 𝗕𝗔𝗡𝗔𝗗𝗜𝗔 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗞𝗢 𝗣𝗥𝗘𝗚𝗡𝗘𝗡𝗧 🤣🤣",
    "𝗦𝗨𝗔𝗥 𝗞𝗘 𝗣𝗜𝗟𝗟𝗘 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧𝗛 𝗠𝗘 𝗦𝗨𝗔𝗥 𝗞𝗔 𝗟𝗢𝗨𝗗𝗔 𝗢𝗥 𝗧𝗘𝗥𝗜 𝗕𝗘‌𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧𝗛 𝗠𝗘 𝗠𝗘𝗥𝗔 𝗟𝗢𝗗𝗔",
    "𝗖𝗛𝗔𝗟 𝗖𝗛𝗔𝗟 𝗔𝗣𝗡𝗜 𝗠𝗔‌𝗔‌𝗞𝗜 𝗖𝗛𝗨𝗖𝗛𝗜𝗬𝗔 𝗗𝗜𝗞𝗔",
    "𝗛𝗔𝗛𝗔𝗛𝗔𝗛𝗔 𝗕𝗔𝗖𝗛𝗛𝗘 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗔𝗞𝗢 𝗖𝗛𝗢𝗗 𝗗𝗜𝗔 𝗡𝗔𝗡𝗚𝗔 𝗞𝗔𝗥𝗞𝗘",
    "𝗧𝗘𝗥𝗜 𝗚𝗙 𝗛𝗘 𝗕𝗔𝗗𝗜 𝗦𝗘𝗫𝗬 𝗨𝗦𝗞𝗢 𝗣𝗜𝗟𝗔𝗞𝗘 𝗖𝗛𝗢𝗢𝗗𝗘𝗡𝗚𝗘 𝗣𝗘𝗣𝗦𝗜",
    "2 𝗥𝗨𝗣𝗔𝗬 𝗞𝗜 𝗣𝗘𝗣𝗦𝗜 𝗧𝗘𝗥𝗜 𝗠𝗨𝗠𝗠𝗬 𝗦𝗔𝗕𝗦𝗘 𝗦𝗘𝗫𝗬 💋💦",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗞𝗢 𝗖𝗛𝗘𝗘𝗠𝗦 𝗦𝗘 𝗖𝗛𝗨𝗗𝗪𝗔𝗩𝗨𝗡𝗚𝗔 𝗠𝗔𝗗𝗘𝗥𝗖𝗛𝗢𝗢𝗗 𝗞𝗘 𝗣𝗜𝗟𝗟𝗘 💦🤣",
    "𝗧𝗘𝗥𝗜 𝗕𝗘‌𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧𝗛 𝗠𝗘 𝗠𝗨𝗧𝗛𝗞𝗘 𝗙𝗔𝗥𝗔𝗥 𝗛𝗢𝗝𝗔𝗩𝗨𝗡𝗚𝗔 𝗛𝗨𝗜 𝗛𝗨𝗜 𝗛𝗨𝗜",
    "𝗦𝗣𝗘𝗘𝗗 𝗟𝗔𝗔𝗔 𝗧𝗘𝗥𝗜 𝗕𝗘‌𝗛𝗘𝗡 𝗖𝗛𝗢𝗗𝗨 𝗥Æ𝗡𝗗𝗜𝗞𝗘 𝗣𝗜𝗟𝗟𝗘 💋💦🤣",
    "𝗧𝗨𝗝𝗛𝗘 𝗔𝗕 𝗧𝗔𝗞 𝗡𝗔𝗛𝗜 𝗦𝗠𝗝𝗛 𝗔𝗬𝗔 𝗞𝗜 𝗠𝗔𝗜 𝗛𝗜 𝗛𝗨 𝗧𝗨𝗝𝗛𝗘 𝗣𝗔𝗜𝗗𝗔 𝗞𝗔𝗥𝗡𝗘 𝗪𝗔𝗟𝗔 𝗕𝗛𝗢𝗦𝗗𝗜𝗞𝗘𝗘 𝗔𝗣𝗡𝗜 𝗠𝗔‌𝗔‌ 𝗦𝗘 𝗣𝗨𝗖𝗛 𝗥Æ𝗡𝗗𝗜 𝗞𝗘 𝗕𝗔𝗖𝗛𝗘𝗘𝗘𝗘 🤩👊👤😍",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗘 𝗕𝗛𝗢𝗦𝗗𝗘 𝗠𝗘𝗜 𝗦𝗣𝗢𝗧𝗜𝗙𝗬 𝗗𝗔𝗟 𝗞𝗘 𝗟𝗢𝗙𝗜 𝗕𝗔𝗝𝗔𝗨𝗡𝗚𝗔 𝗗𝗜𝗡 𝗕𝗛𝗔𝗥 😍🎶🎶💥",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗔 𝗡𝗔𝗬𝗔 𝗥Æ𝗡𝗗𝗜 𝗞𝗛𝗔𝗡𝗔 𝗞𝗛𝗢𝗟𝗨𝗡𝗚𝗔 𝗖𝗛𝗜𝗡𝗧𝗔 𝗠𝗔𝗧 𝗞𝗔𝗥 👊🤣🤣😳",
    "𝗧𝗘𝗥𝗔 𝗕𝗔𝗔𝗣 𝗛𝗨 𝗕𝗛𝗢𝗦𝗗𝗜𝗞𝗘 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗢 𝗥Æ𝗡𝗗𝗜 𝗞𝗛𝗔𝗡𝗘 𝗣𝗘 𝗖𝗛𝗨𝗗𝗪𝗔 𝗞𝗘 𝗨𝗦 𝗣𝗔𝗜𝗦𝗘 𝗞𝗜 𝗗𝗔𝗔𝗥𝗨 𝗣𝗘𝗘𝗧𝗔 𝗛𝗨 🍷🤩🔥",
    "𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 𝗔𝗣𝗡𝗔 𝗕𝗔𝗗𝗔 𝗦𝗔 𝗟𝗢𝗗𝗔 𝗚𝗛𝗨𝗦𝗦𝗔 𝗗𝗨𝗡𝗚𝗔𝗔 𝗞𝗔𝗟𝗟𝗔𝗔𝗣 𝗞𝗘 𝗠𝗔𝗥 𝗝𝗔𝗬𝗘𝗚𝗜 🤩😳😳🔥",
    "𝗧𝗢𝗛𝗔𝗥 𝗠𝗨𝗠𝗠𝗬 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 𝗣𝗨𝗥𝗜 𝗞𝗜 𝗣𝗨𝗥𝗜 𝗞𝗜𝗡𝗚𝗙𝗜𝗦𝗛𝗘𝗥 𝗞𝗜 𝗕𝗢𝗧𝗧𝗟𝗘 𝗗𝗔𝗟 𝗞𝗘 𝗧𝗢𝗗 𝗗𝗨𝗡𝗚𝗔 𝗔𝗡𝗗𝗘𝗥 𝗛𝗜 😱😂🤩",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗢 𝗜𝗧𝗡𝗔 𝗖𝗛𝗢𝗗𝗨𝗡𝗚𝗔 𝗞𝗜 𝗦𝗔𝗣𝗡𝗘 𝗠𝗘𝗜 𝗕𝗛𝗜 𝗠𝗘𝗥𝗜 𝗖𝗛𝗨𝗗𝗔𝗜 𝗬𝗔𝗔𝗗 𝗞𝗔𝗥𝗘𝗚𝗜 𝗥Æ𝗡𝗗𝗜 🥳😍👊💥",
    "𝗧𝗘𝗥𝗜 𝗠𝗨𝗠𝗠𝗬 𝗔𝗨𝗥 𝗕𝗔𝗛𝗘𝗡 𝗞𝗢 𝗗𝗔𝗨𝗗𝗔 𝗗𝗔𝗨𝗗𝗔 𝗡𝗘 𝗖𝗛𝗢𝗗𝗨𝗡𝗚𝗔 𝗨𝗡𝗞𝗘 𝗡𝗢 𝗕𝗢𝗟𝗡𝗘 𝗣𝗘 𝗕𝗛𝗜 𝗟𝗔𝗡𝗗 𝗚𝗛𝗨𝗦𝗔 𝗗𝗨𝗡𝗚𝗔 𝗔𝗡𝗗𝗘𝗥 𝗧𝗔𝗞 😎😎🤣🔥",
    "𝗧𝗘𝗥𝗜 𝗠𝗨𝗠𝗠𝗬 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗞𝗢 𝗢𝗡𝗟𝗜𝗡𝗘 𝗢𝗟𝗫 𝗣𝗘 𝗕𝗘𝗖𝗛𝗨𝗡𝗚𝗔 𝗔𝗨𝗥 𝗣𝗔𝗜𝗦𝗘 𝗦𝗘 𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗔 𝗞𝗢𝗧𝗛𝗔 𝗞𝗛𝗢𝗟 𝗗𝗨𝗡𝗚𝗔 😎🤩😝😍",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗘 𝗕𝗛𝗢𝗦𝗗𝗔 𝗜𝗧𝗡𝗔 𝗖𝗛𝗢𝗗𝗨𝗡𝗚𝗔 𝗞𝗜 𝗧𝗨 𝗖𝗔𝗛 𝗞𝗘 𝗕𝗛𝗜 𝗪𝗢 𝗠𝗔𝗦𝗧 𝗖𝗛𝗨𝗗𝗔𝗜 𝗦𝗘 𝗗𝗨𝗥 𝗡𝗛𝗜 𝗝𝗔 𝗣𝗔𝗬𝗘𝗚𝗔𝗔 😏😏🤩😍",
    "𝗦𝗨𝗡 𝗕𝗘 𝗥Æ𝗡𝗗𝗜 𝗞𝗜 𝗔𝗨𝗟𝗔𝗔𝗗 𝗧𝗨 𝗔𝗣𝗡𝗜 𝗕𝗔𝗛𝗘𝗡 𝗦𝗘 𝗦𝗘𝗘𝗞𝗛 𝗞𝗨𝗖𝗛 𝗞𝗔𝗜𝗦𝗘 𝗚𝗔𝗔𝗡𝗗 𝗠𝗔𝗥𝗪𝗔𝗧𝗘 𝗛𝗔𝗜😏🤬🔥💥",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗔 𝗬𝗔𝗔𝗥 𝗛𝗨 𝗠𝗘𝗜 𝗔𝗨𝗥 𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗔 𝗣𝗬𝗔𝗔𝗥 𝗛𝗨 𝗠𝗘𝗜 𝗔𝗝𝗔 𝗠𝗘𝗥𝗔 𝗟𝗔𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 𝗟𝗘 🤩🤣💥",
    "𝗧𝗘𝗥𝗜 𝗕𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘 𝗨𝗦𝗘𝗥𝗕𝗢𝗧 𝗟𝗔𝗚𝗔𝗔𝗨𝗡𝗚𝗔 𝗦𝗔𝗦𝗧𝗘 𝗦𝗣𝗔𝗠 𝗞𝗘 𝗖𝗛𝗢𝗗𝗘",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗚𝗔𝗔𝗡𝗗 𝗠𝗘 𝗦𝗔𝗥𝗜𝗬𝗔 𝗗𝗔𝗔𝗟 𝗗𝗨𝗡𝗚𝗔 𝗠𝗔‌𝗔‌𝗗𝗔𝗥𝗖𝗛Ø𝗗 𝗨𝗦𝗜 𝗦𝗔𝗥𝗜𝗬𝗘 𝗣𝗥 𝗧𝗔𝗡𝗚 𝗞𝗘 𝗕𝗔𝗖𝗛𝗘 𝗣𝗔𝗜𝗗𝗔 𝗛𝗢𝗡𝗚𝗘 😱😱",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘 ✋ 𝗛𝗔𝗧𝗧𝗛 𝗗𝗔𝗟𝗞𝗘 👶 𝗕??𝗖𝗖𝗛𝗘 𝗡𝗜𝗞𝗔𝗟 𝗗𝗨𝗡𝗚𝗔 😍",
    "𝗧𝗘𝗥𝗜 𝗕𝗘𝗛𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘 𝗞𝗘𝗟𝗘 𝗞𝗘 𝗖𝗛𝗜𝗟𝗞𝗘 🤤🤤",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘 𝗦𝗨𝗧𝗟𝗜 𝗕𝗢𝗠𝗕 𝗙𝗢𝗗 𝗗𝗨𝗡𝗚𝗔 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗝𝗛𝗔𝗔𝗧𝗘 𝗝𝗔𝗟 𝗞𝗘 𝗞𝗛𝗔𝗔𝗞 𝗛𝗢 𝗝𝗔𝗬𝗘𝗚𝗜💣💋",
    "𝗧𝗘𝗥𝗜 𝗩𝗔𝗛𝗘𝗘𝗡 𝗞𝗢 𝗛𝗢𝗥𝗟𝗜𝗖𝗞𝗦 𝗣𝗘𝗘𝗟𝗔𝗞𝗘 𝗖𝗛𝗢𝗗𝗨𝗡𝗚𝗔 𝗠𝗔‌𝗔‌𝗗𝗔𝗥𝗖𝗛Ø𝗗😚",
    "𝗧𝗘𝗥𝗜 𝗜𝗧𝗘𝗠 𝗞𝗜 𝗚𝗔𝗔𝗡𝗗 𝗠𝗘 𝗟𝗨𝗡𝗗 𝗗𝗔𝗔𝗟𝗞𝗘,𝗧𝗘𝗥𝗘 𝗝𝗔𝗜𝗦𝗔 𝗘𝗞 𝗢𝗥 𝗡𝗜𝗞𝗔𝗔𝗟 𝗗𝗨𝗡𝗚𝗔 𝗠𝗔‌𝗔‌𝗗𝗔𝗥𝗖𝗛Ø𝗗😆🤤💋",
    "𝗧𝗘𝗥𝗜 𝗩𝗔𝗛𝗘𝗘𝗡 𝗞𝗢 𝗔𝗣𝗡𝗘 𝗟𝗨𝗡𝗗 𝗣𝗥 𝗜𝗧𝗡𝗔 𝗝𝗛𝗨𝗟𝗔𝗔𝗨𝗡𝗚𝗔 𝗞𝗜 𝗝𝗛𝗨𝗟𝗧𝗘 𝗝𝗛𝗨𝗟𝗧𝗘 𝗛𝗜 𝗕𝗔𝗖𝗛𝗔 𝗣𝗔𝗜𝗗𝗔 𝗞𝗥 𝗗𝗘𝗚𝗜 💦💋",
    "𝗦𝗨𝗔𝗥 𝗞𝗘 𝗣𝗜𝗟𝗟𝗘 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗞𝗢 𝗦𝗔𝗗𝗔𝗞 𝗣𝗥 𝗟𝗜𝗧𝗔𝗞𝗘 𝗖𝗛𝗢𝗗 𝗗𝗨𝗡𝗚𝗔 😂😆🤤",
    "𝗔𝗕𝗘 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗞𝗔 𝗕𝗛𝗢𝗦𝗗𝗔 𝗠𝗔𝗗𝗘𝗥𝗖𝗛𝗢𝗢𝗗 𝗞𝗥 𝗣𝗜𝗟𝗟𝗘 𝗣𝗔𝗣𝗔 𝗦𝗘 𝗟𝗔𝗗𝗘𝗚𝗔 𝗧𝗨 😼😂🤤",
    "𝗚𝗔𝗟𝗜 𝗚𝗔𝗟𝗜 𝗡𝗘 𝗦𝗛𝗢𝗥 𝗛𝗘 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗥Æ𝗡𝗗𝗜 𝗖𝗛𝗢𝗥 𝗛𝗘 💋💋💦",
    "𝗔𝗕𝗘 𝗧𝗘𝗥𝗜 𝗕𝗘‌𝗛𝗘𝗡 𝗞𝗢 𝗖𝗛𝗢𝗗𝗨 𝗥Æ𝗡𝗗𝗜𝗞𝗘 𝗣𝗜𝗟𝗟𝗘 𝗞𝗨𝗧𝗧𝗘 𝗞𝗘 𝗖𝗛𝗢𝗗𝗘 😂👻🔥",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗞𝗢 𝗔𝗜𝗦𝗘 𝗖𝗛𝗢𝗗𝗔 𝗔𝗜𝗦𝗘 𝗖𝗛𝗢𝗗𝗔 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗔 𝗕𝗘𝗗 𝗣𝗘𝗛𝗜 𝗠𝗨𝗧𝗛 𝗗𝗜𝗔 💦💦💦💦",
    "𝗧𝗘𝗥𝗜 𝗕𝗘‌𝗛𝗘𝗡 𝗞𝗘 𝗕𝗛𝗢𝗦𝗗𝗘 𝗠𝗘 𝗔𝗔𝗔𝗚 𝗟𝗔𝗚𝗔𝗗𝗜𝗔 𝗠𝗘𝗥𝗔 𝗠𝗢𝗧𝗔 𝗟𝗨𝗡𝗗 𝗗𝗔𝗟𝗞𝗘 🔥🔥💦😆😆",
    "𝗥Æ𝗡𝗗𝗜𝗞𝗘 𝗕𝗔𝗖𝗛𝗛𝗘 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗞𝗢 𝗖𝗛𝗢𝗗𝗨 𝗖𝗛𝗔𝗟 𝗡𝗜𝗞𝗔𝗟",
    "𝗞𝗜𝗧𝗡𝗔 𝗖𝗛𝗢𝗗𝗨 𝗧𝗘𝗥𝗜 𝗥Æ𝗡𝗗𝗜 𝗠𝗔‌𝗔‌𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧𝗛 𝗔𝗕𝗕 𝗔𝗣𝗡𝗜 𝗕𝗘‌𝗛𝗘𝗡 𝗞𝗢 𝗕𝗛𝗘𝗝 😆👻🤤",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗞𝗛𝗢𝗗 𝗞𝗘 𝗨𝗦𝗠𝗘 𝗖𝗬𝗟𝗜𝗡𝗗𝗘𝗥 ⛽️ 𝗙𝗜𝗧 𝗞𝗔𝗥𝗞𝗘 𝗨𝗦𝗠𝗘𝗘 𝗗𝗔𝗟 𝗠𝗔𝗞𝗛𝗔𝗡𝗜 𝗕𝗔𝗡𝗔𝗨𝗡𝗚𝗔𝗔𝗔🤩👊🔥",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 𝗦𝗛𝗘𝗘𝗦𝗛𝗔 𝗗𝗔𝗟 𝗗𝗨𝗡𝗚𝗔𝗔𝗔 𝗔𝗨𝗥 𝗖𝗛𝗔𝗨𝗥𝗔𝗛𝗘 𝗣𝗘 𝗧𝗔𝗔𝗡𝗚 𝗗𝗨𝗡𝗚𝗔 𝗕𝗛𝗢𝗦𝗗𝗜𝗞𝗘😈😱🤩",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 𝗖𝗥𝗘𝗗𝗜𝗧 𝗖𝗔𝗥𝗗 𝗗𝗔𝗟 𝗞𝗘 𝗔𝗚𝗘 𝗦𝗘 500 𝗞𝗘 𝗞𝗔𝗔𝗥𝗘 𝗞𝗔𝗔𝗥𝗘 𝗡𝗢𝗧𝗘 𝗡𝗜𝗞𝗔𝗟𝗨𝗡𝗚𝗔𝗔 𝗕𝗛𝗢𝗦𝗗𝗜𝗞𝗘💰💰🤩",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗘 𝗦𝗔𝗧𝗛 𝗦𝗨𝗔𝗥 𝗞𝗔 𝗦𝗘𝗫 𝗞𝗔𝗥𝗪𝗔 𝗗𝗨𝗡𝗚𝗔𝗔 𝗘𝗞 𝗦𝗔𝗧𝗛 6-6 𝗕𝗔𝗖𝗛𝗘 𝗗𝗘𝗚𝗜💰🔥😱",
    "𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 𝗔𝗣𝗣𝗟𝗘 𝗞𝗔 18𝗪 𝗪𝗔𝗟𝗔 𝗖𝗛𝗔𝗥𝗚𝗘𝗥 🔥🤩",
    "𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗜 𝗚𝗔𝗔𝗡𝗗 𝗠𝗘𝗜 𝗢𝗡𝗘𝗣𝗟𝗨𝗦 𝗞𝗔 𝗪𝗥𝗔𝗣 𝗖𝗛𝗔𝗥𝗚𝗘𝗥 30𝗪 𝗛𝗜𝗚𝗛 𝗣𝗢𝗪𝗘𝗥 💥😂😎",
    "𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗞𝗢 𝗔𝗠𝗔𝗭𝗢𝗡 𝗦𝗘 𝗢𝗥𝗗𝗘𝗥 𝗞𝗔𝗥𝗨𝗡𝗚𝗔 10 𝗿𝘀 𝗠𝗘𝗜 𝗔𝗨𝗥 𝗙𝗟𝗜𝗣𝗞𝗔𝗥𝗧 𝗣𝗘 20 𝗥𝗦 𝗠𝗘𝗜 𝗕𝗘𝗖𝗛 𝗗𝗨𝗡𝗚𝗔🤮👿😈🤖",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗕𝗔𝗗𝗜 𝗕𝗛𝗨𝗡𝗗 𝗠𝗘 𝗭𝗢𝗠𝗔𝗧𝗢 𝗗𝗔𝗟 𝗞𝗘 𝗦𝗨𝗕𝗪𝗔𝗬 𝗞𝗔 𝗕𝗙𝗙 𝗩𝗘𝗚 𝗦𝗨𝗕 𝗖𝗢𝗠𝗕𝗢 [15𝗰𝗺 , 16 𝗶𝗻𝗰𝗵𝗲𝘀 ] 𝗢𝗥𝗗𝗘𝗥 𝗖𝗢𝗗 𝗞𝗥𝗩𝗔𝗨𝗡𝗚𝗔 𝗢𝗥 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗝𝗔𝗕 𝗗𝗜𝗟𝗜𝗩𝗘𝗥𝗬 𝗗𝗘𝗡𝗘 𝗔𝗬𝗘𝗚𝗜 𝗧𝗔𝗕 𝗨𝗦𝗣𝗘 𝗝𝗔𝗔𝗗𝗨 𝗞𝗥𝗨𝗡𝗚𝗔 𝗢𝗥 𝗙𝗜𝗥 9 𝗠𝗢𝗡𝗧𝗛 𝗕𝗔𝗔𝗗 𝗩𝗢 𝗘𝗞 𝗢𝗥 𝗙𝗥𝗘𝗘 𝗗𝗜𝗟𝗜𝗩𝗘𝗥𝗬 𝗗𝗘𝗚𝗜🙀👍🥳🔥",
    "𝗧𝗘𝗥𝗜 𝗕𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗞𝗔𝗔𝗟𝗜🙁🤣💥",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘 𝗖𝗛𝗔𝗡𝗚𝗘𝗦 𝗖𝗢𝗠𝗠𝗜𝗧 𝗞𝗥𝗨𝗚𝗔 𝗙𝗜𝗥 𝗧𝗘𝗥𝗜 𝗕𝗛𝗘𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗔𝗨𝗧𝗢𝗠𝗔𝗧𝗜𝗖𝗔𝗟𝗟𝗬 𝗨𝗣𝗗𝗔𝗧𝗘 𝗛𝗢𝗝𝗔𝗔𝗬𝗘𝗚𝗜🤖🙏🤔",
    "𝗧𝗘𝗥𝗜 𝗠𝗔𝗨𝗦𝗜 𝗞𝗘 𝗕𝗛𝗢𝗦𝗗𝗘 𝗠𝗘𝗜 𝗜𝗡𝗗𝗜𝗔𝗡 𝗥𝗔𝗜𝗟𝗪𝗔𝗬 🚂💥😂",
    "𝗧𝗨 𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗧𝗘𝗥𝗔 𝗞𝗛𝗔𝗡𝗗𝗔𝗡 𝗦𝗔𝗕 𝗕𝗔𝗛𝗘𝗡 𝗞𝗘 𝗟𝗔𝗪𝗗𝗘 𝗥Æ𝗡𝗗𝗜 𝗛𝗔𝗜 𝗥Æ𝗡𝗗𝗜 🤢✅🔥",
    "𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 𝗜𝗢𝗡𝗜𝗖 𝗕𝗢𝗡𝗗 𝗕𝗔𝗡𝗔 𝗞𝗘 𝗩𝗜𝗥𝗚𝗜𝗡𝗜𝗧𝗬 𝗟𝗢𝗢𝗦𝗘 𝗞𝗔𝗥𝗪𝗔 𝗗𝗨𝗡𝗚𝗔 𝗨𝗦𝗞𝗜 📚 😎🤩",
    "𝗧𝗘𝗥𝗜 𝗥Æ𝗡𝗗𝗜 𝗠𝗔‌𝗔‌ 𝗦𝗘 𝗣𝗨𝗖𝗛𝗡𝗔 𝗕𝗔𝗔𝗣 𝗞𝗔 𝗡𝗔𝗔𝗠 𝗕𝗔𝗛𝗘𝗡 𝗞𝗘 𝗟𝗢𝗗𝗘𝗘𝗘𝗘𝗘 🤩🥳😳",
    "𝗧𝗨 𝗔𝗨𝗥 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗗𝗢𝗡𝗢 𝗞𝗜 𝗕𝗛𝗢𝗦𝗗𝗘 𝗠𝗘𝗜 𝗠𝗘𝗧𝗥𝗢 𝗖𝗛𝗔𝗟𝗪𝗔 𝗗𝗨𝗡𝗚𝗔 𝗠𝗔𝗗𝗔𝗥𝗫𝗛𝗢𝗗 🚇🤩😱🥶",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗢 𝗜𝗧𝗡𝗔 𝗖𝗛𝗢𝗗𝗨𝗡𝗚𝗔 𝗧𝗘𝗥𝗔 𝗕𝗔𝗔𝗣 𝗕𝗛𝗜 𝗨𝗦𝗞𝗢 𝗣𝗔𝗛𝗖𝗛𝗔𝗡𝗔𝗡𝗘 𝗦𝗘 𝗠𝗔𝗡𝗔 𝗞𝗔𝗥 𝗗𝗘𝗚𝗔😂👿🤩",
    "𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗘 𝗕𝗛𝗢𝗦𝗗𝗘 𝗠𝗘𝗜 𝗛𝗔𝗜𝗥 𝗗𝗥𝗬𝗘𝗥 𝗖𝗛𝗔𝗟𝗔 𝗗𝗨𝗡𝗚𝗔𝗔💥🔥🔥",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 𝗧𝗘𝗟𝗘𝗚𝗥𝗔𝗠 𝗞𝗜 𝗦𝗔𝗥𝗜 𝗥Æ𝗡𝗗𝗜𝗬𝗢𝗡 𝗞𝗔 𝗥Æ𝗡𝗗𝗜 𝗞𝗛𝗔𝗡𝗔 𝗞𝗛𝗢𝗟 𝗗𝗨𝗡𝗚𝗔𝗔👿🤮😎",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗔𝗟𝗘𝗫𝗔 𝗗𝗔𝗟 𝗞𝗘𝗘 𝗗𝗝 𝗕𝗔𝗝𝗔𝗨𝗡𝗚𝗔𝗔𝗔 🎶 ⬆️🤩💥",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗘 𝗕𝗛𝗢𝗦𝗗𝗘 𝗠𝗘𝗜 𝗚𝗜𝗧𝗛𝗨𝗕 𝗗𝗔𝗟 𝗞𝗘 𝗔𝗣𝗡𝗔 𝗕𝗢𝗧 𝗛𝗢𝗦𝗧 𝗞𝗔𝗥𝗨𝗡𝗚𝗔𝗔 🤩👊👤😍",
    "𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗔 𝗩𝗣𝗦 𝗕𝗔𝗡𝗔 𝗞𝗘 24*7 𝗕𝗔𝗦𝗛 𝗖𝗛𝗨𝗗𝗔𝗜 𝗖𝗢𝗠𝗠𝗔𝗡𝗗 𝗗𝗘 𝗗𝗨𝗡𝗚𝗔𝗔 🤩💥🔥🔥",
    "𝗧𝗘𝗥𝗜 𝗠𝗨𝗠𝗠𝗬 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 𝗧𝗘𝗥𝗘 𝗟𝗔𝗡𝗗 𝗞𝗢 𝗗𝗔𝗟 𝗞𝗘 𝗞𝗔𝗔𝗧 𝗗𝗨𝗡𝗚𝗔 𝗠𝗔‌𝗔‌𝗗𝗔𝗥𝗖𝗛Ø𝗗 🔪😂🔥",
    "𝗦𝗨𝗡 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗔 𝗕𝗛𝗢𝗦𝗗𝗔 𝗔𝗨𝗥 𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗔 𝗕𝗛𝗜 𝗕𝗛𝗢𝗦𝗗𝗔 👿😎👊",
    "𝗧𝗨𝗝𝗛𝗘 𝗗𝗘𝗞𝗛 𝗞𝗘 𝗧𝗘𝗥𝗜 𝗥Æ𝗡𝗗𝗜 𝗕𝗔𝗛𝗘𝗡 𝗣𝗘 𝗧𝗔𝗥𝗔𝗦 𝗔𝗧𝗔 𝗛𝗔𝗜 𝗠𝗨𝗝𝗛𝗘 𝗕𝗔𝗛𝗘𝗡 𝗞𝗘 𝗟𝗢𝗗𝗘𝗘𝗘𝗘 👿💥🤩🔥",
    "𝗦𝗨𝗡 𝗠𝗔‌𝗔‌𝗗𝗔𝗥𝗖𝗛Ø𝗗 𝗝𝗬𝗔𝗗𝗔 𝗡𝗔 𝗨𝗖𝗛𝗔𝗟 𝗠𝗔‌𝗔‌ 𝗖𝗛𝗢𝗗 𝗗𝗘𝗡𝗚𝗘 𝗘𝗞 𝗠𝗜𝗡 𝗠𝗘𝗜 ✅🤣🔥🤩",
    "𝗔𝗣𝗡𝗜 𝗔𝗠𝗠𝗔 𝗦𝗘 𝗣𝗨𝗖𝗛𝗡𝗔 𝗨𝗦𝗞𝗢 𝗨𝗦 𝗞𝗔𝗔𝗟𝗜 𝗥𝗔𝗔𝗧 𝗠𝗘𝗜 𝗞𝗔𝗨𝗡 𝗖𝗛𝗢𝗗𝗡𝗘𝗘 𝗔𝗬𝗔 𝗧𝗛𝗔𝗔𝗔! 𝗧𝗘𝗥𝗘 𝗜𝗦 𝗣𝗔𝗣𝗔 𝗞𝗔 𝗡𝗔𝗔𝗠 𝗟𝗘𝗚𝗜 😂👿😳",
    "𝗧𝗢𝗛𝗔𝗥 𝗕𝗔𝗛𝗜𝗡 𝗖𝗛𝗢𝗗𝗨 𝗕𝗕𝗔𝗛𝗘𝗡 𝗞𝗘 𝗟𝗔𝗪𝗗𝗘 𝗨𝗦𝗠𝗘 𝗠𝗜𝗧𝗧𝗜 𝗗𝗔𝗟 𝗞𝗘 𝗖𝗘𝗠𝗘𝗡𝗧 𝗦𝗘 𝗕𝗛𝗔𝗥 𝗗𝗨 🏠🤢🤩💥",
    "𝗠𝗔‌𝗔‌𝗗𝗔𝗥𝗖𝗛Ø𝗗 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘 𝗚𝗛𝗨𝗧𝗞𝗔 𝗞𝗛𝗔𝗔𝗞𝗘 𝗧𝗛𝗢𝗢𝗞 𝗗𝗨𝗡𝗚𝗔 🤣🤣",
    "𝗧𝗘𝗥𝗘 𝗕𝗘‌𝗛𝗘𝗡 𝗞 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘 𝗖𝗛𝗔𝗞𝗨 𝗗𝗔𝗔𝗟 𝗞𝗔𝗥 𝗖𝗛𝗨𝗨‌𝗧 𝗞𝗔 𝗞𝗛𝗢𝗢𝗡 𝗞𝗔𝗥 𝗗𝗨𝗚𝗔",
    "𝗧𝗘𝗥𝗜 𝗩𝗔𝗛𝗘𝗘𝗡 𝗡𝗛𝗜 𝗛𝗔𝗜 𝗞𝗬𝗔? 9 𝗠𝗔𝗛𝗜𝗡𝗘 𝗥𝗨𝗞 𝗦𝗔𝗚𝗜 𝗩𝗔𝗛𝗘𝗘𝗡 𝗗𝗘𝗧𝗔 𝗛𝗨 🤣🤣🤩",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞 𝗕𝗛𝗢𝗦𝗗𝗘 𝗠𝗘 𝗔𝗘𝗥𝗢𝗣𝗟𝗔𝗡𝗘𝗣𝗔𝗥𝗞 𝗞𝗔𝗥𝗞𝗘 𝗨𝗗𝗔𝗔𝗡 𝗕𝗛𝗔𝗥 𝗗𝗨𝗚𝗔 ✈️🛫",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘 𝗦𝗨𝗧𝗟𝗜 𝗕𝗢𝗠𝗕 𝗙𝗢𝗗 𝗗𝗨𝗡𝗚𝗔 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗝𝗛𝗔𝗔𝗧𝗘 𝗝𝗔𝗟 𝗞𝗘 𝗞𝗛𝗔𝗔𝗞 𝗛𝗢 𝗝𝗔𝗬𝗘𝗚𝗜💣",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘 𝗦𝗖𝗢𝗢𝗧𝗘𝗥 𝗗𝗔𝗔𝗟 𝗗𝗨𝗚𝗔👅",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗞𝗔𝗞𝗧𝗘 🤱 𝗚𝗔𝗟𝗜 𝗞𝗘 𝗞𝗨𝗧𝗧𝗢 🦮 𝗠𝗘 𝗕𝗔𝗔𝗧 𝗗𝗨𝗡𝗚𝗔 𝗣𝗛𝗜𝗥 🍞 𝗕𝗥𝗘𝗔𝗗 𝗞𝗜 𝗧𝗔𝗥𝗛 𝗞𝗛𝗔𝗬𝗘𝗡𝗚𝗘 𝗪𝗢 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧",
    "𝗗𝗨𝗗𝗛 𝗛𝗜𝗟𝗔𝗔𝗨𝗡𝗚𝗔 𝗧𝗘𝗥𝗜 𝗩𝗔𝗛𝗘𝗘𝗡 𝗞𝗘 𝗨𝗣𝗥 𝗡𝗜𝗖𝗛𝗘 🆙🆒😙",
    "𝗧𝗘𝗥𝗜 𝗕𝗘𝗛𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘 @ll_ALPHA_BABY_lll 𝗞𝗔 𝗟𝗨𝗡𝗗 𝗗𝗔𝗟 𝗗𝗨𝗡𝗚𝗔 𝗙𝗜𝗥 𝗢 𝗣𝗥𝗘𝗚𝗡𝗘𝗡𝗧 𝗛𝗢 𝗝𝗔𝗬𝗘𝗚𝗜 🍌🍌😍",
    "𝗧𝗘𝗥𝗜 𝗩𝗔𝗛𝗘𝗘𝗡 𝗗𝗛𝗔𝗡𝗗𝗛𝗘 𝗩𝗔𝗔𝗟𝗜 😋😛",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗘 𝗕𝗛𝗢𝗦𝗗𝗘 𝗠𝗘 𝗔𝗖 𝗟𝗔𝗚𝗔 𝗗𝗨𝗡𝗚𝗔 𝗦𝗔𝗔𝗥𝗜 𝗚𝗔𝗥𝗠𝗜 𝗡𝗜𝗞𝗔𝗟 𝗝𝗔𝗔𝗬𝗘𝗚𝗜",
    "𝗧𝗘𝗥𝗜 𝗩𝗔𝗛𝗘𝗘𝗡 𝗞𝗢 𝗛𝗢𝗥𝗟𝗜𝗖𝗞𝗦 𝗣𝗘𝗘𝗟𝗔𝗨𝗡𝗚𝗔 𝗠𝗔‌𝗔‌𝗗𝗔𝗥𝗖𝗛Ø𝗗😚",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗢 𝗞𝗢𝗟𝗞𝗔𝗧𝗔 𝗩𝗔𝗔𝗟𝗘 𝗝𝗜𝗧𝗨 𝗕𝗛𝗔𝗜𝗬𝗔 𝗞𝗔 𝗟𝗨𝗡𝗗 𝗠𝗨𝗕𝗔𝗥𝗔𝗞 🤩🤩",
    "𝗧𝗘𝗥𝗜 𝗠𝗨𝗠𝗠𝗬 𝗞𝗜 𝗙𝗔𝗡𝗧𝗔𝗦𝗬 𝗛𝗨 𝗟𝗔𝗪𝗗𝗘, 𝗧𝗨 𝗔𝗣𝗡𝗜 𝗕𝗛𝗘𝗡 𝗞𝗢 𝗦𝗠𝗕𝗛𝗔𝗔𝗟 😈😈",
    "𝗧𝗘𝗥𝗔 𝗣𝗘𝗛𝗟𝗔 𝗕𝗔𝗔𝗣 𝗛𝗨 𝗠𝗔‌𝗔‌𝗗𝗔𝗥𝗖𝗛Ø𝗗 ",
    "𝗧𝗘𝗥𝗜 𝗩𝗔𝗛𝗘𝗘𝗡 𝗞𝗘 𝗕𝗛𝗢𝗦𝗗𝗘 𝗠𝗘 𝗫𝗩𝗜𝗗𝗘𝗢𝗦.𝗖𝗢𝗠 𝗖𝗛𝗔𝗟𝗔 𝗞𝗘 𝗠𝗨𝗧𝗛 𝗠𝗔‌𝗔‌𝗥𝗨𝗡𝗚𝗔 🤡😹",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗔 𝗚𝗥𝗢𝗨𝗣 𝗩𝗔𝗔𝗟𝗢𝗡 𝗦𝗔𝗔𝗧𝗛 𝗠𝗜𝗟𝗞𝗘 𝗚𝗔𝗡𝗚 𝗕𝗔𝗡𝗚 𝗞𝗥𝗨𝗡𝗚𝗔🙌🏻☠️ ",
    "𝗧𝗘𝗥𝗜 𝗜𝗧𝗘𝗠 𝗞𝗜 𝗚𝗔𝗔𝗡𝗗 𝗠𝗘 𝗟𝗨𝗡𝗗 𝗗𝗔𝗔𝗟𝗞𝗘,𝗧𝗘𝗥𝗘 𝗝𝗔𝗜𝗦𝗔 𝗘𝗞 𝗢𝗥 𝗡𝗜𝗞𝗔𝗔𝗟 𝗗𝗨𝗡𝗚𝗔 𝗠𝗔‌𝗔‌𝗗𝗔𝗥𝗖𝗛Ø𝗗🤘🏻🙌🏻☠️ ",
    "𝗔𝗨𝗞𝗔𝗔𝗧 𝗠𝗘 𝗥𝗘𝗛 𝗩𝗥𝗡𝗔 𝗚𝗔𝗔𝗡𝗗 𝗠𝗘 𝗗𝗔𝗡𝗗𝗔 𝗗𝗔𝗔𝗟 𝗞𝗘 𝗠𝗨𝗛 𝗦𝗘 𝗡𝗜𝗞𝗔𝗔𝗟 𝗗𝗨𝗡𝗚𝗔 𝗦𝗛𝗔𝗥𝗜𝗥 𝗕𝗛𝗜 𝗗𝗔𝗡𝗗𝗘 𝗝𝗘𝗦𝗔 𝗗𝗜𝗞𝗛𝗘𝗚𝗔 🙄🤭🤭",
    "𝗧𝗘𝗥𝗜 𝗠𝗨𝗠𝗠𝗬 𝗞𝗘 𝗦𝗔𝗔𝗧𝗛 𝗟𝗨𝗗𝗢 𝗞𝗛𝗘𝗟𝗧𝗘 𝗞𝗛𝗘𝗟𝗧𝗘 𝗨𝗦𝗞𝗘 𝗠𝗨𝗛 𝗠𝗘 𝗔𝗣𝗡𝗔 𝗟𝗢𝗗𝗔 𝗗𝗘 𝗗𝗨𝗡𝗚𝗔☝🏻☝🏻😬",
    "𝗧𝗘𝗥𝗜 𝗩𝗔𝗛𝗘𝗘𝗡 𝗞𝗢 𝗔𝗣𝗡𝗘 𝗟𝗨𝗡𝗗 𝗣𝗥 𝗜𝗧𝗡𝗔 𝗝𝗛𝗨𝗟𝗔𝗔𝗨𝗡𝗚𝗔 𝗞𝗜 𝗝𝗛𝗨𝗟𝗧𝗘 𝗝𝗛𝗨𝗟𝗧𝗘 𝗛𝗜 𝗕𝗔𝗖𝗛𝗔 𝗣𝗔𝗜𝗗𝗔 𝗞𝗥 𝗗𝗘𝗚𝗜👀👯 ",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 𝗕𝗔𝗧𝗧𝗘𝗥𝗬 𝗟𝗔𝗚𝗔 𝗞𝗘 𝗣𝗢𝗪𝗘??𝗕𝗔𝗡𝗞 𝗕??𝗡𝗔 𝗗𝗨𝗡??𝗔 🔋 🔥🤩",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 𝗖++ 𝗦𝗧𝗥𝗜𝗡𝗚 𝗘𝗡𝗖𝗥𝗬𝗣𝗧𝗜𝗢𝗡 𝗟𝗔𝗚𝗔 𝗗𝗨𝗡𝗚𝗔 𝗕𝗔𝗛𝗧𝗜 𝗛𝗨𝗬𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗥𝗨𝗞 𝗝𝗔𝗬𝗘𝗚𝗜𝗜𝗜𝗜😈🔥😍",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗘 𝗚𝗔𝗔𝗡𝗗 𝗠𝗘𝗜 𝗝𝗛𝗔𝗔𝗗𝗨 𝗗𝗔𝗟 𝗞𝗘 𝗠𝗢𝗥 🦚 𝗕𝗔𝗡𝗔 𝗗𝗨𝗡𝗚𝗔𝗔 🤩🥵😱",
    "𝗧𝗘𝗥𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 𝗦𝗛𝗢𝗨𝗟𝗗𝗘𝗥𝗜𝗡𝗚 𝗞𝗔𝗥 𝗗𝗨𝗡𝗚𝗔𝗔 𝗛𝗜𝗟𝗔𝗧𝗘 𝗛𝗨𝗬𝗘 𝗕𝗛𝗜 𝗗𝗔𝗥𝗗 𝗛𝗢𝗚𝗔𝗔𝗔😱🤮👺",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗢 𝗥𝗘𝗗𝗜 𝗣𝗘 𝗕𝗔𝗜𝗧𝗛𝗔𝗟 𝗞𝗘 𝗨𝗦𝗦𝗘 𝗨𝗦𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗕𝗜𝗟𝗪𝗔𝗨𝗡𝗚𝗔𝗔 💰 😵🤩",
    "𝗕𝗛𝗢𝗦𝗗𝗜𝗞𝗘 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 4 𝗛𝗢𝗟𝗘 𝗛𝗔𝗜 𝗨𝗡𝗠𝗘 𝗠𝗦𝗘𝗔𝗟 𝗟𝗔𝗚𝗔 𝗕𝗔𝗛𝗨𝗧 𝗕𝗔𝗛𝗘𝗧𝗜 𝗛𝗔𝗜 𝗕𝗛𝗢𝗙𝗗𝗜𝗞𝗘👊🤮🤢🤢",
    "𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 𝗕𝗔𝗥𝗚𝗔𝗗 𝗞𝗔 𝗣𝗘𝗗 𝗨𝗚𝗔 𝗗𝗨𝗡𝗚𝗔𝗔 𝗖𝗢𝗥𝗢𝗡𝗔 𝗠𝗘𝗜 𝗦𝗔𝗕 𝗢𝗫𝗬𝗚𝗘𝗡 𝗟𝗘𝗞𝗔𝗥 𝗝𝗔𝗬𝗘𝗡𝗚𝗘🤢🤩🥳",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 𝗦𝗨𝗗𝗢 𝗟𝗔𝗚𝗔 𝗞𝗘 𝗕𝗜𝗚𝗦𝗣𝗔𝗠 𝗟𝗔𝗚𝗔 𝗞𝗘 9999 𝗙𝗨𝗖𝗞 𝗟𝗔𝗚𝗔𝗔 𝗗𝗨 🤩🥳🔥",
    "𝗧𝗘𝗥𝗜 𝗩𝗔𝗛𝗘𝗡 𝗞𝗘 𝗕𝗛𝗢𝗦𝗗𝗜𝗞𝗘 𝗠𝗘𝗜 𝗕𝗘𝗦𝗔𝗡 𝗞𝗘 𝗟𝗔𝗗𝗗𝗨 𝗕𝗛𝗔𝗥 𝗗𝗨𝗡𝗚𝗔🤩🥳🔥😈",
]

# ===================== GLOBALS =====================
authorized_users = {}
authorized_groups = {}
active_operations = {}
muted_users = {}
raid_history = {}
rate_limits = {}
last_message_time = {}
saved_stickers = []  # List to store saved sticker IDs

# ===================== FILE HANDLING =====================
def load_data():
    global authorized_users, authorized_groups, muted_users, raid_history, saved_stickers
    
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r') as f:
                data = json.load(f)
                authorized_users = data.get('users', {})
                for owner_id in OWNER_ID:
                    if str(owner_id) not in authorized_users:
                        authorized_users[str(owner_id)] = {
                            'authorized': True,
                            'username': 'Owner',
                            'first_name': 'Owner',
                            'auth_date': datetime.now().isoformat(),
                            'is_owner': True,
                            'added_by': 'system'
                        }
            print(f"✅ Loaded {len(authorized_users)} authorized users")
        
        if os.path.exists(GROUPS_FILE):
            with open(GROUPS_FILE, 'r') as f:
                authorized_groups = json.load(f)
            print(f"✅ Loaded {len(authorized_groups)} authorized groups")
        
        if os.path.exists(MUTED_USERS_FILE):
            with open(MUTED_USERS_FILE, 'r') as f:
                muted_users = json.load(f)
            print(f"✅ Loaded {len(muted_users)} muted users")
        
        if os.path.exists(RAID_HISTORY_FILE):
            with open(RAID_HISTORY_FILE, 'r') as f:
                raid_history = json.load(f)
            print(f"✅ Loaded raid history")
        
        # Load saved stickers
        if os.path.exists(STICKERS_FILE):
            with open(STICKERS_FILE, 'r') as f:
                saved_stickers = json.load(f)
            print(f"✅ Loaded {len(saved_stickers)} saved stickers")
            
    except Exception as e:
        print(f"❌ Load error: {e}")
        authorized_users = {}
        authorized_groups = {}
        muted_users = {}
        raid_history = {}
        saved_stickers = []

def save_data():
    try:
        # Save users
        with open(USERS_FILE, 'w') as f:
            json.dump({'users': authorized_users}, f, indent=2)
        
        # Save groups
        with open(GROUPS_FILE, 'w') as f:
            json.dump(authorized_groups, f, indent=2)
        
        # Save muted users
        with open(MUTED_USERS_FILE, 'w') as f:
            json.dump(muted_users, f, indent=2)
        
        # Save raid history
        with open(RAID_HISTORY_FILE, 'w') as f:
            json.dump(raid_history, f, indent=2)
        
        # Save stickers
        with open(STICKERS_FILE, 'w') as f:
            json.dump(saved_stickers, f, indent=2)
            
    except Exception as e:
        print(f"❌ Save error: {e}")

def save_sticker(sticker_id: str) -> bool:
    """Save a sticker ID to the stickers file"""
    try:
        if sticker_id not in saved_stickers:
            saved_stickers.append(sticker_id)
            with open(STICKERS_FILE, 'w') as f:
                json.dump(saved_stickers, f, indent=2)
            print(f"✅ Saved sticker: {sticker_id[:20]}...")
            return True
        else:
            print(f"⚠️ Sticker already saved: {sticker_id[:20]}...")
            return False
    except Exception as e:
        print(f"❌ Save sticker error: {e}")
        return False

def remove_sticker(sticker_id: str) -> bool:
    """Remove a sticker ID from saved stickers"""
    try:
        if sticker_id in saved_stickers:
            saved_stickers.remove(sticker_id)
            with open(STICKERS_FILE, 'w') as f:
                json.dump(saved_stickers, f, indent=2)
            print(f"✅ Removed sticker: {sticker_id[:20]}...")
            return True
        else:
            print(f"⚠️ Sticker not found: {sticker_id[:20]}...")
            return False
    except Exception as e:
        print(f"❌ Remove sticker error: {e}")
        return False

load_data()

# ===================== USER MANAGEMENT FUNCTIONS =====================
async def add_user_by_id(user_id: int, context, chat_id: int) -> bool:
    """Add user to authorized users"""
    try:
        # Get user info
        try:
            user = await context.bot.get_chat(user_id)
            username = user.username or ""
            first_name = user.first_name or "User"
        except:
            username = ""
            first_name = f"User_{user_id}"
        
        # Add to authorized users
        authorized_users[str(user_id)] = {
            'authorized': True,
            'username': username,
            'first_name': first_name,
            'auth_date': datetime.now().isoformat(),
            'is_owner': user_id in OWNER_ID,
            'added_by': OWNER_ID[0],
            'added_date': datetime.now().isoformat()
        }
        
        save_data()
        
        # Send special message
        await context.bot.send_message(
            chat_id=chat_id,
            text="🦅 AAJ SE TU MADARA KA BHAI 🦅\n\n"
        )
        
        # Also notify the user if possible
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text="🦅 AAJ SE TU MADARA KA BHAI 🦅\n\n"
            )
        except:
            pass
            
        return True
        
    except Exception as e:
        print(f"Add user error: {e}")
        return False

async def remove_user_by_id(user_id: int, context, chat_id: int) -> bool:
    """Remove user from authorized users"""
    try:
        user_id_str = str(user_id)
        
        if user_id in OWNER_ID:
            await context.bot.send_message(
                chat_id=chat_id,
                text="❌ You cannot remove yourself as owner!"
            )
            return False
        
        if user_id_str not in authorized_users:
            await context.bot.send_message(
                chat_id=chat_id,
                text="❌ User not found in authorized list!"
            )
            return False
        
        # Get user info before removing
        user_info = authorized_users[user_id_str]
        username = user_info.get('username', '')
        first_name = user_info.get('first_name', f'User_{user_id}')
        
        # Remove user
        del authorized_users[user_id_str]
        save_data()
        
        # Send special message
        await context.bot.send_message(
            chat_id=chat_id,
            text="💀 NIKAL BLK JAKA MADARA KO FHIR PAPA BOL 💀\n\n"
        )
        
        # Also notify the user if possible
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text="💀 NIKAL BLK JAKA MADARA KO FHIR PAPA BOL 💀\n\n"
            )
        except:
            pass
            
        return True
        
    except Exception as e:
        print(f"Remove user error: {e}")
        return False

# ===================== HELPER FUNCTIONS =====================
def check_authorized(user_id: int) -> bool:
    user_id_str = str(user_id)
    return user_id_str in authorized_users and authorized_users[user_id_str].get('authorized', False)

def is_owner(user_id: int) -> bool:
    return user_id in OWNER_ID

def add_group_access(chat_id: int, title: str = "", added_by: int = 0) -> bool:
    try:
        authorized_groups[str(chat_id)] = {
            'authorized': True,
            'title': title,
            'added_by': added_by,
            'added_date': datetime.now().isoformat()
        }
        save_data()
        return True
    except Exception as e:
        print(f"Add group error: {e}")
        return False

def is_muted(chat_id: int, user_id: int) -> bool:
    chat_str = str(chat_id)
    user_str = str(user_id)
    return chat_str in muted_users and user_str in muted_users[chat_str]
def mute_user(chat_id: int, user_id: int) -> bool:
    try:
        chat_str = str(chat_id)
        user_str = str(user_id)
        
        if chat_str not in muted_users:
            muted_users[chat_str] = []
        
        if user_str not in muted_users[chat_str]:
            muted_users[chat_str].append(user_str)
            save_data()
        return True
    except Exception as e:
        print(f"Mute error: {e}")
        return False

def unmute_user(chat_id: int, user_id: int) -> bool:
    try:
        chat_str = str(chat_id)
        user_str = str(user_id)
        
        if chat_str in muted_users and user_str in muted_users[chat_str]:
            muted_users[chat_str].remove(user_str)
            save_data()
        return True
    except Exception as e:
        print(f"Unmute error: {e}")
        return False

def log_raid_attempt(attacker_id: int, target_id: int, chat_id: int):
    """Log raid attempts for anti-raid protection"""
    try:
        attacker_str = str(attacker_id)
        target_str = str(target_id)
        chat_str = str(chat_id)
        
        if chat_str not in raid_history:
            raid_history[chat_str] = {}
        
        if attacker_str not in raid_history[chat_str]:
            raid_history[chat_str][attacker_str] = {
                'last_attempt': datetime.now().isoformat(),
                'targets': [],
                'count': 0
            }
        
        raid_history[chat_str][attacker_str]['last_attempt'] = datetime.now().isoformat()
        raid_history[chat_str][attacker_str]['count'] += 1
        
        if target_str not in raid_history[chat_str][attacker_str]['targets']:
            raid_history[chat_str][attacker_str]['targets'].append(target_str)
        
        save_data()
    except Exception as e:
        print(f"Raid log error: {e}")

def check_rate_limit(chat_id: int, user_id: int) -> bool:
    """Check if user is rate limited"""
    key = f"{chat_id}_{user_id}"
    current_time = time.time()
    
    if key not in rate_limits:
        rate_limits[key] = []
    
    # Remove old entries (last 60 seconds)
    rate_limits[key] = [t for t in rate_limits[key] if current_time - t < 60]
    
    # Check if user has sent too many messages
    if len(rate_limits[key]) >= 50:  # Max 50 messages per minute per user
        return False
    
    rate_limits[key].append(current_time)
    return True

def should_auto_back_raid(attacker_id: int, chat_id: int) -> bool:
    """Check if auto-back-raid should trigger"""
    if attacker_id in OWNER_ID:
        return False
    
    chat_str = str(chat_id)
    attacker_str = str(attacker_id)
    
    if chat_str in raid_history and attacker_str in raid_history[chat_str]:
        raid_data = raid_history[chat_str][attacker_str]
        
        # Check if attacker targeted owner
        for owner_id in OWNER_ID:
            if str(owner_id) in raid_data.get('targets', []):
                # Check if recent attack (within last 5 minutes)
                last_attempt = datetime.fromisoformat(raid_data['last_attempt'])
                time_diff = (datetime.now() - last_attempt).total_seconds()
                
                if time_diff < 300:  # 5 minutes
                    return True
    
    return False

# ===================== MESSAGE HANDLING =====================
async def send_message_safely(context, chat_id: int, message: str, reply_to: int = None) -> bool:
    """Send message with flood protection"""
    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_to_message_id=reply_to
        )
        await asyncio.sleep(MESSAGE_DELAY)
        return True
    except RetryAfter as e:
        await asyncio.sleep(e.retry_after + 1)
        return False
    except Exception:
        return False
async def send_sticker_safely(context, chat_id: int, sticker_id: str) -> bool:
    """Send sticker with flood protection"""
    try:
        await context.bot.send_sticker(
            chat_id=chat_id,
            sticker=sticker_id
        )
        await asyncio.sleep(STICKER_DELAY)
        return True
    except RetryAfter as e:
        await asyncio.sleep(e.retry_after + 1)
        return False
    except Exception:
        return False

# ===================== WORKER FUNCTIONS =====================
async def raid_worker(chat_id: int, target_name: str, target_user_id: int, count: int, context, attacker_id: int):
    """RAID WORKER WITH ANTI-RAID PROTECTION"""
    # ANTI-RAID CHECK: Don't raid owner
    if target_user_id in OWNER_ID:
        await context.bot.send_message(
            chat_id=chat_id,
            text="BAAP PE RAID KARAGA MADARCHOD? FIR TOH TERA GAND MA RAID HI HO JAYEGA! 😈",
            reply_to_message_id=attacker_id
        )
        return
    
    # Log raid attempt
    log_raid_attempt(attacker_id, target_user_id, chat_id)
    
    sent = 0
    failed = 0
    start_time = time.time()
    
    chat_id_str = str(chat_id)
    active_operations[chat_id_str] = {'type': 'raid', 'stop': False}
    
    try:
        # Send initial status
        await send_message_safely(context, chat_id, 
            f"TERI MUMMY KO CHODNE KA SAMAY SHURU HOTA HAI!😈\n")
        
        # Send raid messages
        for i in range(count):
            if active_operations.get(chat_id_str, {}).get('stop', False):
                break
            
            try:
                msg = random.choice(RAID_MESSAGES)
                text = f"[{target_name}](tg://user?id={target_user_id}) {msg}"
                
                success = await send_message_safely(context, chat_id, text)
                if success:
                    sent += 1
                else:
                    failed += 1
                    
                # Progress update
                if sent % 20 == 0 and sent > 0:
                    elapsed = time.time() - start_time
                    speed = sent / elapsed if elapsed > 0 else 0
                    await send_message_safely(context, chat_id,
                        f"📊 Progress: {sent}/{count} ({speed:.1f} msg/sec)")
                    
            except Exception:
                failed += 1
                await asyncio.sleep(1)
        
        # Completion message
        elapsed_time = time.time() - start_time
        speed = sent / elapsed_time if elapsed_time > 0 else 0
        
        completion_msg = f"CHUD GAYA MADARCHOD!{target_name}!"
        
        await send_message_safely(context, chat_id,
            f"MADARA KO BAAP BOL NAHI TO AUR CHUDAGA")
        
    except Exception as e:
        print(f"Raid error: {e}")
        await send_message_safely(context, chat_id, f"❌ RAID ERROR**\nSent: {sent}")
    finally:
        if chat_id_str in active_operations:
            del active_operations[chat_id_str]

async def sticker_worker(chat_id: int, count: int, context, update_id: int):
    """STICKER SPAM WORKER"""
    sent = 0
    failed = 0
    start_time = time.time()
    
    chat_id_str = str(chat_id)
    active_operations[chat_id_str] = {'type': 'sticker', 'stop': False}
    
    try:
        await send_message_safely(context, chat_id,
            f"MUTHI KA SAMAY SHURU HOTA HAI!😈\n")
        
        # Send stickers
        for i in range(count):
            if active_operations.get(chat_id_str, {}).get('stop', False):
                break
            
            try:
                # Random sticker from saved stickers
                if saved_stickers:
                    sticker_id = random.choice(saved_stickers)
                    success = await send_sticker_safely(context, chat_id, sticker_id)
                    if success:
                        sent += 1
                    else:
                        failed += 1
                else:
                    await send_message_safely(context, chat_id, 
                        "❌ No stickers saved yet!\nReply to any sticker with `.addsticker` to save it.")
                    break
                    
                # Progress update
                if sent % 15 == 0 and sent > 0:
                    elapsed = time.time() - start_time
                    speed = sent / elapsed if elapsed > 0 else 0
                    await send_message_safely(context, chat_id,
                        f"📊 Sticker Progress: {sent}/{count} ({speed:.1f} sticker/sec)")
                    
            except Exception:
                failed += 1
                await asyncio.sleep(1)
        
        # Completion
        elapsed_time = time.time() - start_time
        speed = sent / elapsed_time if elapsed_time > 0 else 0
        
        await send_message_safely(context, chat_id,
            f"AUR MARAGA MUTHI")
        
    except Exception as e:
        print(f"Sticker error: {e}")
        await send_message_safely(context, chat_id, f"❌ **STICKER ERROR**\nSent: {sent}")
    finally:
        if chat_id_str in active_operations:
            del active_operations[chat_id_str]

async def spam_worker(chat_id: int, text: str, count: int, context, update_id: int):
    """SPAM WORKER"""
    sent = 0
    failed = 0
    start_time = time.time()
    
    chat_id_str = str(chat_id)
    active_operations[chat_id_str] = {'type': 'spam', 'stop': False}
    
    try:
        await send_message_safely(context, chat_id,
            f"LODA CHODA")
        
        for i in range(count):
            if active_operations.get(chat_id_str, {}).get('stop', False):
                break
            
            try:
                success = await send_message_safely(context, chat_id, text)
                if success:
                    sent += 1
                else:
                    failed += 1
                    
                if sent % 20 == 0 and sent > 0:
                    elapsed = time.time() - start_time
                    speed = sent / elapsed if elapsed > 0 else 0
                    await send_message_safely(context, chat_id,
                        f"📊 Progress: {sent}/{count} ({speed:.1f} msg/sec)")
                    
            except Exception:
                failed += 1
                await asyncio.sleep(1)
        
        elapsed_time = time.time() - start_time
        speed = sent / elapsed_time if elapsed_time > 0 else 0
        
        await send_message_safely(context, chat_id,
            f"HALA KHATAM")
        
    except Exception as e:
        print(f"Spam error: {e}")
        await send_message_safely(context, chat_id, f"❌ **SPAM ERROR**\nSent: {sent}")
    finally:
        if chat_id_str in active_operations:
            del active_operations[chat_id_str]

async def auto_back_raid(attacker_id: int, chat_id: int, context):
    """AUTO BACK RAID when someone raids owner"""
    if attacker_id in OWNER_ID:
        return
    
    try:
        # Get attacker info
        attacker = await context.bot.get_chat(attacker_id)
        attacker_name = attacker.first_name or "User"
        
        # Send warning
        await send_message_safely(context, chat_id,
            f"🛡 **ANTI-RAID ACTIVATED**\n⚡️ Auto-back-raid initiated on {attacker_name}!")
        
        # Start back raid
        asyncio.create_task(
            raid_worker(
                chat_id,
                attacker_name,
                attacker_id,
                100,  # Back raid with 100 messages
                context,
                OWNER_ID[0]  # Bot owner is the attacker for back raid
            )
        )
        
    except Exception as e:
        print(f"Auto back raid error: {e}")

# ===================== COMMAND HANDLERS =====================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    user_id = update.effective_user.id
    
    # AUTO ACCESS TO ALL GROUPS
    if update.effective_chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        add_group_access(
            update.effective_chat.id,
            update.effective_chat.title or f"Group {update.effective_chat.id}",
            user_id
        )
    
    if not check_authorized(user_id):
        keyboard = [
            [InlineKeyboardButton("🔑 Get Access", callback_data=f"auth_{ACCESS_CODE}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🔒 **ULTIMATE RAID BOT 🦅🛡⚡️\n\n"
            f"Use /auth {ACCESS_CODE} to get access\n\n"
            f"Commands:**\n"
            f"• `.raid [count]` - Raid user (reply to user)\n"
            f"• `.spam [count] [text]` - Spam text\n"
            f"• `.sticker [count]` - Spam stickers\n"
            f"• `.addsticker` - Save sticker (reply to sticker)\n"
            f"• `.removesticker` - Remove sticker (reply to sticker)\n"
            f"• `.liststickers` - Show saved stickers\n"
            f"• `/mute` - Mute user (reply)\n"
            f"• `/unmute` - Unmute user (reply)\n"
            f"• `.stop` - Stop operations\n"
            f"• `/status` - Check status\n\n"
            f"**Owner Commands:**\n"
            f"• `.adduser [id]` - Add user\n"
            f"• `.removeuser [id]` - Remove user\n"
            f"• `/listusers` - List all users\n\n"
            f"**Features:**\n"
            f"• 🦅 MADARA family system\n"
            f"• 🛡 Anti-raid protection\n"
            f"• ⚡️ Auto-back-raid system\n"
            f"• 🏷 Save ANY sticker for spam\n"
            f"• 🔇 Mute/Unmute users\n"
            f"• ✅ Auto-group access\n"
            f"• 🚫 No admin needed\n\n"
            f"**How to use:**\n"
            f"1. Reply to any sticker with `.addsticker`\n"
            f"2. Use `.sticker 50` to spam saved stickers\n"
            f"3. Reply to user: `.raid 100`",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text("✅ **AUTHORIZED USER - All commands ready!")

async def auth_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Auth command handler"""
    user_id = update.effective_user.id
    
    if len(context.args) == 1 and context.args[0] == ACCESS_CODE:
        username = update.effective_user.username or ""
        first_name = update.effective_user.first_name or "User"
        
        authorized_users[str(user_id)] = {
            'authorized': True,
            'username': username,
            'first_name': first_name,
            'auth_date': datetime.now().isoformat(),
            'is_owner': is_owner(user_id)
        }
        save_data()
        
        await update.message.reply_text(
            "🦅 AAJ SE TU MADARA KA BHAI 🦅\n\n"
            "✅ ACCESS GRANTED! All features unlocked!\n"
            "🎯 Welcome to the MADARA family!"
        )
    else:
        await update.message.reply_text("❌ Invalid Access Code")
async def mute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mute user command"""
    if not check_authorized(update.effective_user.id):
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("📌 Reply to a user to mute them")
        return
    
    target_user = update.message.reply_to_message.from_user
    chat_id = update.effective_chat.id
    
    if mute_user(chat_id, target_user.id):
        # Try to restrict user in group
        try:
            if update.effective_chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
                await context.bot.restrict_chat_member(
                    chat_id=chat_id,
                    user_id=target_user.id,
                    permissions=ChatPermissions(
                        can_send_messages=False,
                        can_send_media_messages=False,
                        can_send_other_messages=False,
                        can_add_web_page_previews=False
                    )
                )
        except:
            pass  # Bot might not have admin rights
        
        await update.message.reply_text(f"🔇 MUTED {target_user.first_name} AAB CHUP HOJA MKC")
    else:
        await update.message.reply_text("❌ Failed to mute user")

async def unmute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unmute user command"""
    if not check_authorized(update.effective_user.id):
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("📌 Reply to a user to unmute them")
        return
    
    target_user = update.message.reply_to_message.from_user
    chat_id = update.effective_chat.id
    
    if unmute_user(chat_id, target_user.id):
        # Try to unrestrict user in group
        try:
            if update.effective_chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
                await context.bot.restrict_chat_member(
                    chat_id=chat_id,
                    user_id=target_user.id,
                    permissions=ChatPermissions(
                        can_send_messages=True,
                        can_send_media_messages=True,
                        can_send_other_messages=True,
                        can_add_web_page_previews=True
                    )
                )
        except:
            pass
        
        await update.message.reply_text(f"🔊 UNMUTED {target_user.first_name}BHOK LE MKC")
    else:
        await update.message.reply_text("❌ Failed to unmute user")

# ===================== MESSAGE HANDLER FOR DOT COMMANDS =====================
async def handle_dot_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all dot commands (.raid, .spam, .sticker, etc.)"""
    if not update.message or not update.message.text:
        return
    
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    text = update.message.text.strip()
    
    print(f"📨 Processing message from {user_id}: {text}")
    
    # Check authorization
    if not check_authorized(user_id):
        print(f"❌ User {user_id} not authorized")
        return
    
    # Auto-group access
    if update.effective_chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        if str(chat_id) not in authorized_groups:
            add_group_access(
                chat_id,
                update.effective_chat.title or f"Group {chat_id}",
                user_id
            )
            print(f"✅ Auto-added group {chat_id}")
    
    # ========== HANDLE .RAID COMMAND ==========
    if text.startswith('.raid'):
        print(f"🎯 RAID command detected: {text}")
        
        if not update.message.reply_to_message:
            await update.message.reply_text("📌 Reply to a user first!\nUsage: .raid 100")
            return
        
        # Parse count
        parts = text.split()
        if len(parts) < 2:
            count = 100
        else:
            try:
                count = int(parts[1])
                count = min(count, MAX_RAID_COUNT)
                count = max(1, count)  # Ensure at least 1
            except ValueError:
                await update.message.reply_text("❌ Invalid number! Use: .raid 100")
                return
        
        target_user = update.message.reply_to_message.from_user
        target_id = target_user.id
        target_name = target_user.first_name or "User"
        
        print(f"🎯 Target: {target_name} (ID: {target_id}), Count: {count}")
        
        await update.message.reply_text(f"MADARA PAPA KI JAI")
        
        asyncio.create_task(
            raid_worker(
                chat_id,
                target_name,
                target_id,
                count,
                context,
                update.message.message_id
            )
        )
        return
    
    # ========== HANDLE .SPAM COMMAND ==========
    elif text.startswith('.spam'):
        print(f"💥 SPAM command detected: {text}")
        
        parts = text.split()
        if len(parts) < 3:
            await update.message.reply_text("Usage: .spam 50 text")
            return
        
        try:
            count = int(parts[1])
            count = min(count, MAX_SPAM_COUNT)
            count = max(1, count)
            spam_text = " ".join(parts[2:])
            
            await update.message.reply_text(f"HALA KAR AAB MKC x{count}...")
            
            asyncio.create_task(
                spam_worker(
                    chat_id,
                    spam_text,
                    count,
                    context,
                    update.message.message_id
                )
            )
        except ValueError:
            await update.message.reply_text("❌ Invalid number! Use: .spam 50 text")
        return
    
    # ========== HANDLE .STICKER COMMAND ==========
    elif text.startswith('.sticker'):
        print(f"🏷 STICKER command detected: {text}")
        
        parts = text.split()
        if len(parts) < 2:
            count = 50
        else:
            try:
                count = int(parts[1])
                count = min(count, MAX_STICKER_COUNT)
                count = max(1, count)
            except ValueError:
                await update.message.reply_text("❌ Invalid number! Use: .sticker 50")
                return
        
        if not saved_stickers:
            await update.message.reply_text("❌ No stickers saved yet!\nReply to any sticker with .addsticker to save it.")
            return
        
        await update.message.reply_text(f"🔄 Starting sticker spam x{count}...")
        
        asyncio.create_task(
            sticker_worker(
                chat_id,
                count,
                context,
                update.message.message_id
            )
        )
        return
    
    # ========== HANDLE .ADDSTICKER COMMAND ==========
    elif text == '.addsticker':
        print("➕ ADDSTICKER command detected")
        
        if not update.message.reply_to_message or not update.message.reply_to_message.sticker:
            await update.message.reply_text("📌 Reply to a sticker with .addsticker to save it!")
            return
        
        sticker = update.message.reply_to_message.sticker
        sticker_id = sticker.file_id
        
        if save_sticker(sticker_id):
            sticker_emoji = sticker.emoji or "🏷"
            await update.message.reply_text(
                f"✅ STICKER SAVED! {sticker_emoji}\n\n"
                f"🏷 ID: `{sticker_id[:30]}...`\n"
                f"📊 Total Saved: {len(saved_stickers)} stickers\n"
                f"🎯 Use: .sticker 50 to spam saved stickers"
            )
        else:
            await update.message.reply_text("⚠️ This sticker is already saved!")
        return
    
    # ========== HANDLE .REMOVESTICKER COMMAND ==========
    elif text == '.removesticker':
        print("➖ REMOVESTICKER command detected")
        
        if not update.message.reply_to_message or not update.message.reply_to_message.sticker:
            await update.message.reply_text("📌 Reply to a sticker with .removesticker to remove it!")
            return
        sticker = update.message.reply_to_message.sticker
        sticker_id = sticker.file_id
        
        if remove_sticker(sticker_id):
            await update.message.reply_text(
                f"🗑 STICKER REMOVED!**\n"
                f"✅ Sticker removed from spam collection\n"
                f"📊 **Remaining: {len(saved_stickers)} stickers"
            )
        else:
            await update.message.reply_text("⚠️ This sticker was not found in saved stickers!")
        return
    
    # ========== HANDLE .LISTSTICKERS COMMAND ==========
    elif text == '.liststickers':
        print("📋 LISTSTICKERS command detected")
        
        if not saved_stickers:
            await update.message.reply_text("📭 No stickers saved yet!\nReply to any sticker with .addsticker to save it.")
            return
        
        message = f"🏷 SAVED STICKERS: {len(saved_stickers)}\n\n"
        
        for i, sticker_id in enumerate(saved_stickers[:10], 1):
            message += f"{i}. `{sticker_id[:40]}...`\n"
        
        if len(saved_stickers) > 10:
            message += f"\n... and {len(saved_stickers) - 10} more stickers"
        
        message += f"\n\n🎯 Use: .sticker 50 to spam these stickers"
        
        await update.message.reply_text(message)
        return
    
    # ========== HANDLE .STOP COMMAND ==========
    elif text == '.stop':
        print("🛑 STOP command detected")
        
        chat_str = str(chat_id)
        if chat_str in active_operations:
            active_operations[chat_str]['stop'] = True
            await update.message.reply_text("JA MADRACHOD, RUK GAYA SABKUCH! 🛑")
        else:
            await update.message.reply_text("✅ No active operations")
        return
    
    # ========== HANDLE .ADDUSER COMMAND (OWNER ONLY) ==========
    elif text.startswith('.adduser') and is_owner(user_id):
        print(f"👑 ADDUSER command detected: {text}")
        
        parts = text.split()
        if len(parts) < 2:
            await update.message.reply_text("📝 Usage: .adduser [user_id]")
            return
        
        try:
            target_id = int(parts[1])
            success = await add_user_by_id(target_id, context, chat_id)
            if not success:
                await update.message.reply_text("❌ Failed to add user!")
        except ValueError:
            await update.message.reply_text("❌ Invalid user ID!")
        return
    
    # ========== HANDLE .REMOVEUSER COMMAND (OWNER ONLY) ==========
    elif text.startswith('.removeuser') and is_owner(user_id):
        print(f"👑 REMOVEUSER command detected: {text}")
        
        parts = text.split()
        if len(parts) < 2:
            await update.message.reply_text("📝 Usage: .removeuser [user_id]")
            return
        
        try:
            target_id = int(parts[1])
            success = await remove_user_by_id(target_id, context, chat_id)
            if not success:
                await update.message.reply_text("❌ Failed to remove user!")
        except ValueError:
            await update.message.reply_text("❌ Invalid user ID!")
        return
    
    # ========== MONITOR FOR RAIDS ON OWNER ==========
    elif text and any(raid_msg in text for raid_msg in RAID_MESSAGES):
        # Check if owner is mentioned
        for owner_id in OWNER_ID:
            if str(owner_id) in text or (update.message.reply_to_message and 
                update.message.reply_to_message.from_user.id == owner_id):
                
                log_raid_attempt(user_id, owner_id, chat_id)
                
                if should_auto_back_raid(user_id, chat_id):
                    await auto_back_raid(user_id, chat_id, context)
                break
# ===================== OTHER COMMANDS =====================
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Status command"""
    if not check_authorized(update.effective_user.id):
        return
    
    await update.message.reply_text(
        f"📊 ULTIMATE RAID BOT STATUS 🦅\n\n"
        f"• 👥 Users: {len(authorized_users)}\n"
        f"• 👥 Groups: {len(authorized_groups)}\n"
        f"• 🔇 Muted: {sum(len(v) for v in muted_users.values())}\n"
        f"• ⚡️ Active: {len(active_operations)}\n"
        f"• 🦅 MADARA Family: ✅ ACTIVE\n"
        f"• 🛡 Anti-raid: ✅ ACTIVE\n"
        f"• 🔄 Auto-back-raid: ✅ READY\n"
        f"• 🏷 Saved Stickers: {len(saved_stickers)}\n"
        f"• 🚫 Admin needed: ❌ NO\n"
        f"• ⚡️ Speed: 28 msg/sec\n"
        f"• 🟢 Status: ONLINE"
    )

async def listusers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all authorized users (OWNER ONLY)"""
    if not is_owner(update.effective_user.id):
        return
    
    if not authorized_users:
        await update.message.reply_text("📭 No authorized users yet")
        return
    
    message = "🦅 MADARA FAMILY MEMBERS 🦅\n\n"
    
    for user_id, user_info in authorized_users.items():
        owner_badge = "👑 " if user_info.get('is_owner') else "• "
        username = f"@{user_info.get('username')}" if user_info.get('username') else "No username"
        name = user_info.get('first_name', 'User')
        
        # Format date
        added_date = user_info.get('added_date', 'Unknown')
        if added_date != 'Unknown':
            try:
                dt = datetime.fromisoformat(added_date)
                added_date = dt.strftime("%d-%m-%Y")
            except:
                pass
        
        message += f"{owner_badge}{name} ({username})\n"
        message += f"   ID: `{user_id}`\n"
        message += f"   Added: {added_date}\n\n"
    
    message += f"Total Family Members: {len(authorized_users)}"
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

# ===================== CALLBACK QUERY HANDLER =====================
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith('auth_'):
        code = query.data.replace('auth_', '')
        if code == ACCESS_CODE:
            user_id = query.from_user.id
            username = query.from_user.username or ""
            first_name = query.from_user.first_name or "User"
            
            authorized_users[str(user_id)] = {
                'authorized': True,
                'username': username,
                'first_name': first_name,
                'auth_date': datetime.now().isoformat(),
                'is_owner': is_owner(user_id)
            }
            save_data()
            
            await query.edit_message_text(
                "🦅 AAJ SE TU MADARA KA BHAI 🦅\n\n"
                "✅ ACCESS GRANTED! All features unlocked!\n"
                "🎯 Welcome to the MADARA family!"
            )

# ===================== MAIN FUNCTION =====================
def main():
    """Start the bot"""
    print("""
    ╔══════════════════════════════════════════════╗
    ║      ULTIMATE RAID BOT - STICKER SAVER       ║
    ║      SAVE ANY STICKER FOR SPAM!              ║
    ╚══════════════════════════════════════════════╝
    """)
    
    print("🏷 Starting STICKER SAVER RAID BOT...")
    print("="*60)
    print("✅ NEW STICKER FEATURES:")
    print("• Reply to ANY sticker with .addsticker")
    print("• Bot saves sticker ID for spam")
    print("• Use .sticker 50 to spam saved stickers")
    print("• .removesticker to remove sticker")
    print("• .liststickers to view saved stickers")
    print("• No sticker pack IDs needed!")
    print("="*60)
    print("✅ ALL OTHER FEATURES ACTIVE:")
    print("• User management (.adduser/.removeuser)")
    print("• Raid system with anti-raid protection")
    print("• Mute/Unmute users")
    print("• Auto-group access (No admin needed)")
    print("• Auto-back-raid protection")
    print("• MADARA family system")
    print("="*60)
    
    # Create Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("auth", auth_command))
    application.add_handler(CommandHandler("mute", mute_command))
    application.add_handler(CommandHandler("unmute", unmute_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("listusers", listusers_command))
    
    # Add callback query handler
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Add message handler for dot commands - THIS IS THE FIX
    # Using filters.TEXT and checking for dot commands in the text
    application.add_handler(MessageHandler(
        filters.TEXT & filters.Regex(r'^\.'),
        handle_dot_commands
    ))
    
    # Start the bot
    print(f"✅ Bot is running...")
    print(f"👑 Owner IDs: {OWNER_ID}")
    print(f"🔑 Access Code: {ACCESS_CODE}")
    print(f"🦅 MADARA Family: ACTIVE")
    print(f"🛡 Anti-raid: ACTIVE")
    print(f"🏷 Saved Stickers: {len(saved_stickers)}")
    print(f"👥 Current Users: {len(authorized_users)}")
    print("="*60)
    print("\n**COMMANDS WORKING:**")
    print("✅ .raid 100 (reply to user)")
    print("✅ .spam 50 text")
    print("✅ .sticker 50")
    print("✅ .addsticker (reply to sticker)")
    print("✅ .removesticker (reply to sticker)")
    print("✅ .liststickers")
    print("✅ .stop")
    print("✅ .adduser (owner only)")
    print("✅ .removeuser (owner only)")
    print("="*60)
    
def run_bot():
    try:
        loop = asyncio.new_event_loop()   # create a new event loop
        asyncio.set_event_loop(loop)      # set it for current thread
        application.run_polling(drop_pending_updates=True)
    except KeyboardInterrupt:
        print("\n👋 Bot stopped!")
    except Exception as e:
        print(f"❌ Error: {e}")

# -------------------------------
# ✅ NO run_polling here
# main.py will handle running the bot
# -------------------------------




