import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
from dotenv import load_dotenv
import os

# Load env file
load_dotenv()

# Ambil token dan group ID dari environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN")
group_id = os.getenv("GROUP_ID")
if group_id is None:
    raise ValueError("GROUP_ID environment variable is missing.")
ALLOWED_GROUP_ID = int(group_id)


# Inisialisasi bot & dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Dictionary sementara untuk data pemain (nanti bisa diganti DB)
players = {}

# Middleware sederhana: hanya izinkan bot di grup tertentu
@dp.message()
async def restrict_group_access(message: Message):
    if message.chat.type != "supergroup" or message.chat.id != ALLOWED_GROUP_ID:
        return  # Abaikan pesan dari luar grup

    await dp.feed_update(message)  # Teruskan ke handler berikutnya

# Command /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.reply("Welcome to Arises Monarch!\nPlease use /setnickname <your_nickname> to begin.")

# Command /setnickname
@dp.message(Command("setnickname"))
async def cmd_setnickname(message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("Please provide a nickname: /setnickname <your_nickname>")
        return

    nickname = args[1]
    user_id = message.from_user.id

    players[user_id] = {
        "nickname": nickname,
        "level": 1,
        "gold": 100,
        "hp": 100,
    }

    await message.reply(
        f"Nickname set to **{nickname}**!\nUse /profile to check your status.",
        parse_mode="Markdown"
    )

# Command /profile
@dp.message(Command("profile"))
async def cmd_profile(message: Message):
    user_id = message.from_user.id
    if user_id not in players:
        await message.reply("You haven't set your nickname yet. Use /setnickname <nickname> first.")
        return

    profile = players[user_id]
    await message.reply(
        f"👤 *{profile['nickname']}*\n"
        f"💪 Level: {profile['level']}\n"
        f"💰 Gold: {profile['gold']}\n"
        f"❤️ HP: {profile['hp']}",
        parse_mode="Markdown"
    )

# Fungsi utama (entry point)
async def main():
    logging.basicConfig(level=logging.INFO)
    print("""Welcome to
Arises Monarch Game Bot!""")
