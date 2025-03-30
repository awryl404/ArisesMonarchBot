import asyncio
import aiosqlite
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiohttp import web
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TOKEN = os.environ.get("7519236415:AAF61RW8e-sGPNkJKZR5JJDCkq6DZdShrnY")  # Ambil token dari Railway
ALLOWED_TOPIC_ID = int(os.environ.get("ALLOWED_TOPIC_ID", 175))  # ID topik yang diperbolehkan
PORT = int(os.environ.get("PORT", 5000))  # Railway menentukan port secara dinamis
APP_URL = f"https://{os.environ.get('RAILWAY_STATIC_URL', 'localhost')}"  # URL Railway

bot = Bot(token=TOKEN)
dp = Dispatcher()
app = web.Application()

# Database initialization
async def init_db():
    async with aiosqlite.connect("game.db") as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS players (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                gold INTEGER DEFAULT 100,
                monarch INTEGER DEFAULT 0
            )
        ''')
        await db.commit()

@dp.message(CommandStart()) 
async def start_game(message: Message):
    if message.message_thread_id and message.message_thread_id != ALLOWED_TOPIC_ID:
        await message.reply("❌ Game ini hanya bisa dimainkan dalam satu topik tertentu!")
        return

    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"

    async with aiosqlite.connect("game.db") as db:
        async with db.execute("SELECT * FROM players WHERE user_id = ?", (user_id,)) as cursor:
            player = await cursor.fetchone()

        if not player:
            await db.execute("INSERT INTO players (user_id, username) VALUES (?, ?)", (user_id, username))
            await db.commit()
            await message.reply(f"👑 Selamat datang di *Arises Monarch*, @{username}!\n\nGunakan /help untuk melihat daftar perintah.")
        else:
            await message.reply(f"👋 Selamat datang kembali, @{username}! Lanjutkan petualanganmu! ⚔")

@dp.message(Command("help"))
async def show_help(message: Message):
    help_text = """
🎮 Arises Monarch - Command List 🎮
/profile - Lihat status karakter
/inventory - Cek item yang kamu miliki
/battle - Mulai pertarungan PvE
/duel @username - Tantang pemain lain dalam PvP
/shop - Beli item atau upgrade
/dungeon - Masuk ke dungeon dan lawan boss
/revive - Gunakan item revive jika mati
/leaderboard - Lihat ranking pemain terbaik
"""
    await message.reply(help_text, parse_mode="Markdown")

async def on_startup(app):
    await bot.set_webhook(url=f"{APP_URL}/webhook/{TOKEN}")
    await init_db()

async def handle_webhook(request):
    if request.match_info.get("token") != TOKEN:
        return web.Response(status=403)
    
    request_data = await request.json()
    update = types.Update(**request_data)
    await dp.feed_update(bot=bot, update=update)
    return web.Response()

async def main():
    app.router.add_post(f"/webhook/{TOKEN}", handle_webhook)
    app.on_startup.append(on_startup)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)  # Menggunakan PORT dari Railway
    await site.start()
    
    await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())