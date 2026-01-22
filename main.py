import os
import aiohttp
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

LANGS = {
    "en": "English",
    "ru": "Русский",
    "de": "Deutsch",
    "uk": "Українська",
    "es": "Español"
}

user_lang = {}

@dp.message(Command("start"))
async def start(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=name, callback_data=f"lang_{code}")]
        for code, name in LANGS.items()
    ])
    await message.answer("🌍 Choose language / Выберите язык:", reply_markup=kb)

@dp.callback_query(lambda c: c.data.startswith("lang_"))
async def set_lang(callback: types.CallbackQuery):
    lang = callback.data.split("_")[1]
    user_lang[callback.from_user.id] = lang
    await callback.message.edit_text("🔍 Send movie title:")

@dp.message()
async def search_movie(message: types.Message):
    query = message.text
    lang = user_lang.get(message.from_user.id, "en")

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.themoviedb.org/3/search/movie",
            params={
                "api_key": TMDB_API_KEY,
                "query": query,
                "language": lang
            }
        ) as resp:
            data = await resp.json()

    if not data["results"]:
        await message.answer("❌ Not found")
        return

    movie = data["results"][0]
    title = movie["title"]
    overview = movie.get("overview", "No description")
    year = movie.get("release_date", "")[:4]

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Netflix", url=f"https://www.netflix.com/search?q={title}"),
            InlineKeyboardButton(text="Prime", url=f"https://www.amazon.com/s?k={title}")
        ],
        [
            InlineKeyboardButton(text="Apple TV", url=f"https://tv.apple.com/search?term={title}"),
            InlineKeyboardButton(text="Disney+", url=f"https://www.disneyplus.com/search?q={title}")
        ],
        [
            InlineKeyboardButton(text="ZDF", url=f"https://www.zdf.de/suche?q={title}")
        ]
    ])

    await message.answer(
        f"🎬 <b>{title}</b> ({year})\n\n{overview}",
        parse_mode="HTML",
        reply_markup=kb
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
