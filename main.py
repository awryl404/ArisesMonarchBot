import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv

# === Load environment variables ===
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")

if not BOT_TOKEN:
    raise ValueError("Missing BOT_TOKEN in environment variables.")
if not GROUP_ID:
    raise ValueError("Missing GROUP_ID in environment variables.")

try:
    ALLOWED_GROUP_ID = int(GROUP_ID)
except ValueError:
    raise ValueError("GROUP_ID must be an integer.")

# === Bot setup ===
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Data pemain sementara (akan diganti database nanti)
players = {}

# === Middleware manual untuk batasi akses ke grup ===
@dp.message()
async def restrict_to_group(message: types.Message):
    if message.chat.id != ALLOWED_GROUP_ID:
        return  # Abaikan pesan dari luar grup
    await dp.feed_update(message)

# === Command Handlers ===
@dp.message(Command("start"))
async def handle_start(message: types.Message):
    await message.reply("👑 Welcome to *Arises Monarch*!\nUse /setnickname <nickname> to begin.", parse_mode="Markdown")

@dp.message(Command("setnickname"))
async def handle_setnickname(message: types.Message):
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

    await message.reply(f"✅ Nickname set to *{nickname}*!\nUse /profile to view your stats.", parse_mode="Markdown")

@dp.message(Command("profile"))
async def handle_profile(message: types.Message):
    user_id = message.from_user.id
    if user_id not in players:
        await message.reply("You haven't set a nickname yet.\nUse /setnickname <nickname>")
        return

    data = players[user_id]
    profile = (
        f"👤 *{data['nickname']}*\n"
        f"💪 Level: {data['level']}\n"
        f"💰 Gold: {data['gold']}\n"
        f"❤️ HP: {data['hp']}"
    )
    await message.reply(profile, parse_mode="Markdown")

# === Entry point ===
async def main():
    logging.basicConfig(level=logging.INFO)
    print("✅ Bot is starting via Railway...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
