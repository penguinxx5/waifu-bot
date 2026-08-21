import asyncio
import json
import random
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_USERNAME = "tsuyaki"
REQUIRED_CHANNEL = "@AnimelarGR"
WAIFU_INTERVAL = 300

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

RARITIES = {
    "Common": {"chance": 40, "coins": 100, "emoji": "⚪", "shop_price": 500},
    "Rare": {"chance": 25, "coins": 200, "emoji": "🟢", "shop_price": 1000},
    "Super Rare": {"chance": 15, "coins": 250, "emoji": "🔵", "shop_price": 1500},
    "Epic": {"chance": 10, "coins": 400, "emoji": "🟣", "shop_price": 2500},
    "Mythic": {"chance": 5, "coins": 500, "emoji": "🟠", "shop_price": 4000},
    "Legendary": {"chance": 3, "coins": 700, "emoji": "🟡", "shop_price": 6000},
    "Ultra Legendary": {"chance": 2, "coins": 1000, "emoji": "🔴", "shop_price": 10000}
}

WAIFUS = [
    {"name": "hinata", "display_name": "Hinata", "anime": "Naruto", "rarity": "Rare"},
    {"name": "rem", "display_name": "Rem", "anime": "Re:Zero", "rarity": "Epic"},
    {"name": "mikasa", "display_name": "Mikasa", "anime": "Attack on Titan", "rarity": "Legendary"},
    {"name": "zero two", "display_name": "Zero Two", "anime": "Darling in the Franxx", "rarity": "Mythic"},
    {"name": "nezuko", "display_name": "Nezuko", "anime": "Demon Slayer", "rarity": "Super Rare"}
]

current_waifu = None
data = {"groups": [], "users": {}}

def get_user(user_id):
    user_id = str(user_id)
    if user_id not in data["users"]:
        data["users"][user_id] = {"coins": 0, "waifus": {}}
    return data["users"][user_id]

def select_rarity():
    rand = random.randint(1, 100)
    cumulative = 0
    for rarity, info in RARITIES.items():
        cumulative += info["chance"]
        if rand <= cumulative:
            return rarity
    return "Common"

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user = get_user(message.from_user.id)
    await message.answer(f"🎌 <b>Botga xush kelibsiz!</b>\n💰 Coinlaringiz: {user['coins']}", parse_mode=ParseMode.HTML)

@dp.message(Command("mywaifus"))
async def cmd_mywaifus(message: types.Message):
    user = get_user(message.from_user.id)
    if not user["waifus"]:
        await message.answer("Sizda hali hech qanday waifu yo'q!")
        return
    text = "\n".join([f"{w['display_name']} x{c}" for w, c in user["waifus"].items()])
    await message.answer(f"💖 Waifularingiz:\n{text}")

@dp.message(Command("guess"))
async def cmd_guess(message: types.Message):
    global current_waifu
    if not current_waifu:
        await message.answer("Hozircha hech qanday waifu yo'q. Kuting!")
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2 or args[1].strip().lower() != current_waifu["name"]:
        await message.answer("❌ Noto'g'ri! Qayta urinib ko'ring.")
        return
    
    user = get_user(message.from_user.id)
    r_info = RARITIES[current_waifu["rarity"]]
    user["coins"] += r_info["coins"]
    name = current_waifu["name"]
    user["waifus"][name] = user["waifus"].get(name, 0) + 1
    
    count = user["waifus"][name]
    await message.answer(f"🎉 Tabriklaymiz! Siz <b>{current_waifu['display_name']}</b>ni qo'lga kiritdingiz! (x{count})\n+{r_info['coins']} coin", parse_mode=ParseMode.HTML)
    current_waifu = None

async def send_waifu():
    global current_waifu
    if not data["groups"]: 
        return
    r = select_rarity()
    w_list = [w for w in WAIFUS if w["rarity"] == r]
    current_waifu = random.choice(w_list if w_list else WAIFUS)
    r_info = RARITIES[current_waifu["rarity"]]
    
    text = (f"🎌 <b>Yangi waifu paydo bo'ldi!</b>\n\n"
            f"Bu qaysi anime qizi?\n"
            f"🎭 Rarity: {r_info['emoji']} {current_waifu['rarity']}\n"
            f"💰 Mukofot: {r_info['coins']} coin\n\n"
            f"Javob: /guess <ism>")
    
    for gid in data["groups"]:
        try:
            await bot.send_photo(gid, "https://via.placeholder.com/400x600.png?text=Anime+Waifu", caption=text, parse_mode=ParseMode.HTML)
        except Exception as e:
            logger.error(f"Xatolik: {e}")

async def scheduler():
    while True:
        await send_waifu()
        await asyncio.sleep(WAIFU_INTERVAL)

async def main():
    asyncio.create_task(scheduler())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
