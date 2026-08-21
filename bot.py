import asyncio
import json
import random
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode, ChatMemberStatus, ChatType
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_USERNAME = "tsuyaki"
REQUIRED_CHANNEL = "@AnimelarGR"
WAIFU_INTERVAL = 300  # 5 minut

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Rarity tizimi
RARITIES = {
    "Common": {"chance": 40, "coins": 50, "emoji": "⚪", "shop_price": 500},
    "Rare": {"chance": 25, "coins": 100, "emoji": "🟢", "shop_price": 1000},
    "Super Rare": {"chance": 15, "coins": 200, "emoji": "🔵", "shop_price": 1500},
    "Epic": {"chance": 10, "coins": 250, "emoji": "🟣", "shop_price": 2500},
    "Mythic": {"chance": 5, "coins": 400, "emoji": "🟠", "shop_price": 4000},
    "Legendary": {"chance": 3, "coins": 500, "emoji": "🟡", "shop_price": 6000},
    "Ultra Legendary": {"chance": 2, "coins": 700, "emoji": "🔴", "shop_price": 10000}
}

# 15 ta anime waifu
WAIFUS = [
    {"name": "hinata", "display_name": "Hinata", "anime": "Naruto", "rarity": "Rare"},
    {"name": "rem", "display_name": "Rem", "anime": "Re:Zero", "rarity": "Epic"},
    {"name": "emilia", "display_name": "Emilia", "anime": "Re:Zero", "rarity": "Epic"},
    {"name": "mikasa", "display_name": "Mikasa", "anime": "Attack on Titan", "rarity": "Legendary"},
    {"name": "asuna", "display_name": "Asuna", "anime": "Sword Art Online", "rarity": "Super Rare"},
    {"name": "zero two", "display_name": "Zero Two", "anime": "Darling in the Franxx", "rarity": "Mythic"},
    {"name": "nezuko", "display_name": "Nezuko", "anime": "Demon Slayer", "rarity": "Super Rare"},
    {"name": "chika", "display_name": "Chika", "anime": "Kaguya-sama", "rarity": "Common"},
    {"name": "mai", "display_name": "Mai", "anime": "Bunny Girl Senpai", "rarity": "Rare"},
    {"name": "makima", "display_name": "Makima", "anime": "Chainsaw Man", "rarity": "Legendary"},
    {"name": "power", "display_name": "Power", "anime": "Chainsaw Man", "rarity": "Super Rare"},
    {"name": "yor", "display_name": "Yor", "anime": "Spy x Family", "rarity": "Epic"},
    {"name": "marin", "display_name": "Marin", "anime": "My Dress-Up Darling", "rarity": "Mythic"},
    {"name": "nagisa", "display_name": "Nagisa", "anime": "Clannad", "rarity": "Common"},
    {"name": "saber", "display_name": "Saber", "anime": "Fate/Stay Night", "rarity": "Ultra Legendary"}
]

current_waifu = None
data = {"groups": [], "users": {}}

def save_data():
    pass

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

async def check_subscription(user_id: int) -> bool:
    """Foydalanuvchi kanalga obuna bo'lganini tekshiradi"""
    try:
        member = await bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        return member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]
    except Exception as e:
        logger.error(f"Kanal tekshirishda xatolik: {e}")
        return False

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if message.chat.type != ChatType.PRIVATE:
        await message.answer("❌ Bu buyruq faqat botning shaxsiy chatida ishlaydi!")
        return
    
    user = get_user(message.from_user.id)
    await message.answer(
        f"🎌 <b>Anime Waifu Botiga xush kelibsiz!</b>\n\n"
        f"💰 Coinlaringiz: <b>{user['coins']}</b>\n\n"
        f"📋 <b>Buyruqlar:</b>\n"
        f"/info - Bot haqida\n"
        f"/mywaifus - Mening waifularim\n"
        f"/mycoins - Coin miqdori\n"
        f"/balance - Coin miqdori\n"
        f"/shop - Do'kon\n"
        f"/givecoin - Coin berish\n"
        f"/giftwaifu - Waifu sovg'a qilish\n"
        f"/ega - Bot egasi\n\n"
        f"⚙️ <b>Guruh uchun:</b>\n"
        f"/setgroup - Guruhni ro'yxatga olish\n\n"
        f"🎮 <b>O'yin:</b>\n"
        f"Har 5 minutda guruhga waifu tashlanadi.\n"
        f"Birinchi bo'lib topgan odam uni qo'lga kiritadi!\n"
        f"Javob: /guess <waifu_ismi>",
        parse_mode=ParseMode.HTML
    )

@dp.message(Command("info"))
async def cmd_info(message: types.Message):
    if message.chat.type != ChatType.PRIVATE:
        await message.answer("❌ Bu buyruq faqat botning shaxsiy chatida ishlaydi!")
        return
    
    await message.answer(
        f"🎌 <b>Anime Waifu Bot</b>\n\n"
        f"Har 5 minutda guruhga tasodifiy waifu tashlanadi.\n"
        f"Birinchi bo'lib topgan odam uni qo'lga kiritadi!\n\n"
        f"🎯 <b>Rarity tizimi:</b>\n"
        f"⚪ Common - 50 coin (40%)\n"
        f"🟢 Rare - 100 coin (25%)\n"
        f"🔵 Super Rare - 200 coin (15%)\n"
        f"🟣 Epic - 250 coin (10%)\n"
        f"🟠 Mythic - 400 coin (5%)\n"
        f"🟡 Legendary - 500 coin (3%)\n"
        f"🔴 Ultra Legendary - 700 coin (2%)\n\n"
        f"👑 Ega: @{OWNER_USERNAME}",
        parse_mode=ParseMode.HTML
    )

@dp.message(Command("ega"))
async def cmd_ega(message: types.Message):
    if message.chat.type != ChatType.PRIVATE:
        await message.answer("❌ Bu buyruq faqat botning shaxsiy chatida ishlaydi!")
        return
    
    await message.answer(f"👑 Ega: @{OWNER_USERNAME}")

@dp.message(Command("balance", "mycoins"))
async def cmd_balance(message: types.Message):
    if message.chat.type != ChatType.PRIVATE:
        await message.answer("❌ Bu buyruq faqat botning shaxsiy chatida ishlaydi!")
        return
    
    user = get_user(message.from_user.id)
    await message.answer(f"💰 Sizning coinlaringiz: <b>{user['coins']}</b>", parse_mode=ParseMode.HTML)

@dp.message(Command("mywaifus"))
async def cmd_mywaifus(message: types.Message):
    if message.chat.type != ChatType.PRIVATE:
        await message.answer("❌ Bu buyruq faqat botning shaxsiy chatida ishlaydi!")
        return
    
    user = get_user(message.from_user.id)
    if not user["waifus"]:
        await message.answer("Sizda hali hech qanday waifu yo'q!")
        return
    
    waifus_list = []
    for waifu_name, count in user["waifus"].items():
        waifu_info = next((w for w in WAIFUS if w["name"] == waifu_name), None)
        if waifu_info:
            rarity_emoji = RARITIES[waifu_info["rarity"]]["emoji"]
            display_text = f"{waifu_info['display_name']} x{count}" if count > 1 else waifu_info['display_name']
            waifus_list.append(f"{rarity_emoji} {display_text} ({waifu_info['anime']})")
    
    total_waifus = sum(user["waifus"].values())
    await message.answer(
        f"💖 <b>Sizning waifularingiz ({total_waifus} ta):</b>\n\n" + "\n".join(waifus_list),
        parse_mode=ParseMode.HTML
    )

@dp.message(Command("shop"))
async def cmd_shop(message: types.Message):
    if message.chat.type != ChatType.PRIVATE:
        await message.answer("❌ Bu buyruq guruhda ishlamaydi!\nBotning shaxsiy chatida yozing.")
        return
    
    user = get_user(message.from_user.id)
    
    shop_list = []
    for w in WAIFUS:
        rarity_info = RARITIES[w["rarity"]]
        shop_list.append(f"{rarity_info['emoji']} {w['display_name']} ({w['anime']}) - <b>{rarity_info['shop_price']} coin</b>")
    
    await message.answer(
        f"🛍️ <b>Do'kon</b>\n\n💰 Sizning coinlaringiz: <b>{user['coins']}</b>\n\n" + 
        "\n".join(shop_list) + 
        "\n\n💡 <b>Sotib olish:</b> /buy <ism>\nMasalan: /buy hinata",
        parse_mode=ParseMode.HTML
    )

@dp.message(Command("buy"))
async def cmd_buy(message: types.Message):
    if message.chat.type != ChatType.PRIVATE:
        await message.answer("❌ Bu buyruq guruhda ishlamaydi!\nBotning shaxsiy chatida yozing.")
        return
    
    user = get_user(message.from_user.id)
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        await message.answer("❌ Format: /buy <waifu_ismi>\nMasalan: /buy hinata")
        return
    
    waifu_name = args[1].strip().lower()
    waifu_info = next((w for w in WAIFUS if w["name"] == waifu_name), None)
    
    if not waifu_info:
        await message.answer("❌ Bunday waifu mavjud emas!\n/shop - barcha waifular ro'yxati")
        return
    
    price = RARITIES[waifu_info["rarity"]]["shop_price"]
    
    if user["coins"] < price:
        await message.answer(
            f"❌ Yetarli coin yo'q!\n"
            f"Kerak: {price} coin\n"
            f"Sizda: {user['coins']} coin"
        )
        return
    
    user["coins"] -= price
    user["waifus"][waifu_name] = user["waifus"].get(waifu_name, 0) + 1
    
    await message.answer(
        f"✅ Tabriklaymiz!\n\n"
        f"Siz <b>{waifu_info['display_name']}</b>ni sotib oldingiz!\n"
        f"💰 Narxi: {price} coin\n"
        f"💰 Qolgan coin: {user['coins']}",
        parse_mode=ParseMode.HTML
    )

@dp.message(Command("givecoin"))
async def cmd_givecoin(message: types.Message):
    if message.chat.type != ChatType.PRIVATE:
        await message.answer("❌ Bu buyruq guruhda ishlamaydi!\nBotning shaxsiy chatida yozing.")
        return
    
    giver = get_user(message.from_user.id)
    
    # Reply orqali berish
    if message.reply_to_message:
        receiver_id = message.reply_to_message.from_user.id
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.answer("❌ Format: /givecoin <miqdor>\nMasalan: /givecoin 100")
            return
        try:
            amount = int(args[1])
        except ValueError:
            await message.answer("❌ Miqdor son bo'lishi kerak!")
            return
    # @username orqali berish
    elif message.entities and len(message.entities) > 1:
        args = message.text.split()
        if len(args) < 3:
            await message.answer("❌ Format: /givecoin @username <miqdor>\nMasalan: /givecoin @username 100")
            return
        username = args[1].replace("@", "")
        try:
            amount = int(args[2])
        except ValueError:
            await message.answer("❌ Miqdor son bo'lishi kerak!")
            return
        
        # Username orqali user ID topish
        try:
            chat = await bot.get_chat(f"@{username}")
            receiver_id = chat.id
        except Exception as e:
            await message.answer("❌ Foydalanuvchi topilmadi!")
            return
    else:
        await message.answer("❌ Format:\n/givecoin @username <miqdor>\nYoki reply qilib: /givecoin <miqdor>")
        return
    
    if amount <= 0:
        await message.answer("❌ Miqdor 0 dan katta bo'lishi kerak!")
        return
    
    if giver["coins"] < amount:
        await message.answer(f"❌ Yetarli coin yo'q!\nSizda: {giver['coins']} coin")
        return
    
    receiver = get_user(receiver_id)
    giver["coins"] -= amount
    receiver["coins"] += amount
    
    await message.answer(
        f"✅ Muvaffaqiyatli!\n\n"
        f"Siz <b>{amount}</b> coinni @{receiver_id} ga berdingiz!\n"
        f"💰 Qolgan coin: {giver['coins']}",
        parse_mode=ParseMode.HTML
    )

@dp.message(Command("giftwaifu"))
async def cmd_giftwaifu(message: types.Message):
    if message.chat.type != ChatType.PRIVATE:
        await message.answer("❌ Bu buyruq guruhda ishlamaydi!\nBotning shaxsiy chatida yozing.")
        return
    
    giver = get_user(message.from_user.id)
    
    # Reply orqali berish
    if message.reply_to_message:
        receiver_id = message.reply_to_message.from_user.id
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.answer("❌ Format: /giftwaifu <waifu_ismi>\nMasalan: /giftwaifu hinata")
            return
        waifu_name = args[1].strip().lower()
    # @username orqali berish
    elif message.entities and len(message.entities) > 1:
        args = message.text.split()
        if len(args) < 3:
            await message.answer("❌ Format: /giftwaifu @username <waifu_ismi>\nMasalan: /giftwaifu @username hinata")
            return
        username = args[1].replace("@", "")
        waifu_name = args[2].strip().lower()
        
        try:
            chat = await bot.get_chat(f"@{username}")
            receiver_id = chat.id
        except Exception as e:
            await message.answer("❌ Foydalanuvchi topilmadi!")
            return
    else:
        await message.answer("❌ Format:\n/giftwaifu @username <waifu_ismi>\nYoki reply qilib: /giftwaifu <waifu_ismi>")
        return
    
    # Waifu mavjudmi?
    waifu_info = next((w for w in WAIFUS if w["name"] == waifu_name), None)
    if not waifu_info:
        await message.answer("❌ Bunday waifu mavjud emas!")
        return
    
    # Beruvchida waifu bormi?
    if waifu_name not in giver["waifus"] or giver["waifus"][waifu_name] == 0:
        await message.answer(f"❌ Sizda <b>{waifu_info['display_name']}</b> yo'q!", parse_mode=ParseMode.HTML)
        return
    
    receiver = get_user(receiver_id)
    
    # Beruvchidan olish
    giver["waifus"][waifu_name] -= 1
    if giver["waifus"][waifu_name] == 0:
        del giver["waifus"][waifu_name]
    
    # Qabul qiluvchiga berish
    receiver["waifus"][waifu_name] = receiver["waifus"].get(waifu_name, 0) + 1
    
    await message.answer(
        f"✅ Muvaffaqiyatli!\n\n"
        f"Siz <b>{waifu_info['display_name']}</b>ni @{receiver_id} ga sovg'a qildingiz!",
        parse_mode=ParseMode.HTML
    )

@dp.message(Command("setgroup"))
async def cmd_setgroup(message: types.Message):
    if message.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        await message.answer("❌ Bu buyruq faqat guruhda ishlaydi!")
        return
    
    try:
        member = await bot.get_chat_member(message.chat.id, message.from_user.id)
        if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
            await message.answer("❌ Bu buyruqni faqat adminlar ishlatishi mumkin!")
            return
    except Exception as e:
        logger.error(f"Admin tekshirishda xatolik: {e}")
        await message.answer("❌ Admin tekshirishda xatolik!")
        return
    
    is_subscribed = await check_subscription(message.from_user.id)
    if not is_subscribed:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Kanalga obuna bo'lish", url=f"https://t.me/{REQUIRED_CHANNEL[1:]}")]
        ])
        await message.answer(
            f"⚠️ Botni ishlatish uchun avval <b>{REQUIRED_CHANNEL}</b> kanaliga obuna bo'ling!",
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
        return
    
    if message.chat.id in data["groups"]:
        await message.answer("❌ Bu guruhga allaqachon bot o'rnatilgan!")
        return
    
    data["groups"].append(message.chat.id)
    await message.answer(
        "✅ <b>Guruh muvaffaqiyatli ro'yxatga olindi!</b>\n\n"
        "Endi har 5 minutda guruhga waifu tashlanadi.\n"
        "Birinchi bo'lib topgan odam uni qo'lga kiritadi!",
        parse_mode=ParseMode.HTML
    )

@dp.message(Command("guess"))
async def cmd_guess(message: types.Message):
    if message.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        await message.answer("❌ Bu buyruq faqat guruhda ishlaydi!")
        return
    
    if message.chat.id not in data["groups"]:
        await message.answer("❌ Bu guruh ro'yxatdan o'tmagan!\n/setgroup - guruhni ro'yxatga olish")
        return
    
    global current_waifu
    
    if not current_waifu:
        await message.answer("❌ Hozircha hech qanday waifu yo'q. Keyingi waifuni kuting!")
        return
    
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("❌ Format: /guess <waifu_ismi>\nMasalan: /guess hinata")
        return
    
    user_guess = args[1].strip().lower()
    
    if user_guess == current_waifu["name"].lower():
        user = get_user(message.from_user.id)
        waifu_info = current_waifu
        rarity_info = RARITIES[waifu_info["rarity"]]
        
        user["coins"] += rarity_info["coins"]
        user["waifus"][waifu_info["name"]] = user["waifus"].get(waifu_info["name"], 0) + 1
        count = user["waifus"][waifu_info["name"]]
        
        count_text = f" x{count}" if count > 1 else ""
        
        await message.answer(
            f"🎉 <b>Tabriklaymiz, {message.from_user.full_name}!</b>\n\n"
            f"Siz <b>{waifu_info['display_name']}</b>ni qo'lga kiritdingiz!{count_text}\n"
            f"🎭 Rarity: {rarity_info['emoji']} {waifu_info['rarity']}\n"
            f"💰 +{rarity_info['coins']} coin\n"
            f"💰 Jami coin: {user['coins']}",
            parse_mode=ParseMode.HTML
        )
        
        current_waifu = None
    else:
        await message.answer("❌ Noto'g'ri! Qayta urinib ko'ring.")

async def send_waifu_to_group():
    global current_waifu
    
    if not data["groups"]:
        return
    
    selected_rarity = select_rarity()
    available_waifus = [w for w in WAIFUS if w["rarity"] == selected_rarity]
    
    if not available_waifus:
        available_waifus = WAIFUS
    
    current_waifu = random.choice(available_waifus)
    rarity_info = RARITIES[current_waifu["rarity"]]
    
    text = (
        f"🎌 <b>Yangi waifu paydo bo'ldi!</b>\n\n"
        f"Bu qaysi anime qizi?\n"
        f"🎭 Rarity: {rarity_info['emoji']} {current_waifu['rarity']}\n"
        f"💰 Mukofot: {rarity_info['coins']} coin\n\n"
        f"Birinchi bo'lib topgan odam uni qo'lga kiritadi!\n"
        f"Javob: /guess <ism>"
    )
    
    for group_id in data["groups"]:
        try:
            await bot.send_photo(
                chat_id=group_id,
                photo="https://via.placeholder.com/400x600.png?text=Anime+Waifu",
                caption=text,
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Guruhga yuborishda xatolik (ID: {group_id}): {e}")

async def waifu_scheduler():
    while True:
        await send_waifu_to_group()
        await asyncio.sleep(WAIFU_INTERVAL)

async def main():
    asyncio.create_task(waifu_scheduler())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
