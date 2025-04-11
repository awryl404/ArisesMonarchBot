import os
import json
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv

# === Load .env ===
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing in environment variables.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

players = {}
TOPIC_FILE = "topic.json"

# === Fungsi bantu simpan dan baca topic ===
def save_topic(group_id: int, topic_id: int):
    try:
        if os.path.exists(TOPIC_FILE):
            with open(TOPIC_FILE, "r") as f:
                data = json.load(f)
        else:
            data = {}

        data[str(group_id)] = topic_id
        with open(TOPIC_FILE, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print("Error saving topic:", e)

def get_topic(group_id: int):
    try:
        if not os.path.exists(TOPIC_FILE):
            return None
        with open(TOPIC_FILE, "r") as f:
            data = json.load(f)
        return data.get(str(group_id))
    except Exception as e:
        print("Error reading topic:", e)
        return None

# === Middleware: batasi berdasarkan group & topic ===
@dp.message()
async def restrict_group_topic(message: types.Message):
    if not message.chat.type in ["supergroup", "group"]:
        return

    topic_id = get_topic(message.chat.id)
    if topic_id is None:
        return  # belum di-bind

    if message.message_thread_id != topic_id:
        return  # salah topik

    await dp.feed_update(message)

# === Command: /bindtopic ===
@dp.message(Command("bindtopic"))
async def bind_topic(message: types.Message):
    if not message.chat.type in ["supergroup", "group"]:
        await message.reply("This command only works in groups.")
        return

    member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if member.status not in ["administrator", "creator"]:
        await message.reply("Only group admins can bind a topic.")
        return

    if message.message_thread_id is None:
        await message.reply("Please use this command *inside a forum topic* (thread).", parse_mode="Markdown")
        return

    save_topic(message.chat.id, message.message_thread_id)
    await message.reply("✅ This topic has been bound for the game.")

# === Command: /start ===
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.reply("👑 Welcome to *Arises Monarch*!\nUse /setnickname <nickname> to begin.", parse_mode="Markdown")

# === Command: /setnickname <name> ===
@dp.message(Command("setnickname"))
async def cmd_nickname(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("Please use: /setnickname <nickname>")
        return

    nickname = args[1]
    user_id = message.from_user.id
    players[user_id] = {
        "nickname": nickname,
        "level": 1,
        "gold": 100,
        "hp": 100
    }

    await message.reply(f"✅ Nickname set to *{nickname}*!", parse_mode="Markdown")

# === Command: /profile ===
@dp.message(Command("profile"))
async def cmd_profile(message: types.Message):
    user_id = message.from_user.id
    if user_id not in players:
        await message.reply("You haven't set a nickname yet.\nUse /setnickname <nickname>")
        return

    p = players[user_id]
    text = (
        f"👤 *{p['nickname']}*\n"
        f"💪 Level: {p['level']}\n"
        f"💰 Gold: {p['gold']}\n"
        f"❤️ HP: {p['hp']}"
    )
    await message.reply(text, parse_mode="Markdown")

# === Start polling ===
async def main():
    logging.basicConfig(level=logging.INFO)
    print("✅ Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
