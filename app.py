import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
import json
import os

# Logging sozlamalari
logging.basicConfig(level=logging.INFO)

# Bot sozlamalari
BOT_TOKEN = "8508263748:AAEoAMxom8nra7cr56X_1nFF3pjqe6e9TaA"  # @BotFather dan olingan token
ADMIN_ID = 7053301759  # Sizning Telegram ID raqamingiz

# Majburiy obuna kanallari (@ belgisiz yoki ID bilan)
CHANNELS = ["@Epic_brand", "@Tarjimabombakinolar"]  # O'z kanallaringizni yozing

# Ma'lumotlar faylini yuklash
DATA_FILE = "movies.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Bot va Dispatcher
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# FSM states
class AddMovie(StatesGroup):
    waiting_for_code = State()
    waiting_for_file = State()

class DeleteMovie(StatesGroup):
    waiting_for_code = State()

# Ma'lumotlar bazasi
movies_db = load_data()

# Foydalanuvchilarning kino ko'rish sonini saqlash
user_movie_count = {}

# Reklamalar ro'yxati (navbat bilan chiqadi)
REKLAMA_LIST = [
    {

        "text": "🎬 <b>Eng zo'r trendagi motion yoki edit kanalni izlayapsizmi?</b>\n\n✨ Unda bu kanal siz uchun!\n\n🎨 Cap Cut Pro ham mavjud!",
        "button_text": "📢 Kanalga o'tish",
        "button_url": "@Epic_brand"
    },
    {
        "photo": "https://i.postimg.cc/example2.jpg",  # 2-reklama rasmi
        "text": "🤖 <b>Yangi kinolar botimiz!</b>\n\n🎥 Eng yangi va sifatli kinolar\n💎 HD sifatda\n⚡️ Tezkor yuklash",
        "button_text": "🤖 Botga o'tish",
        "button_url": "@Tarjimabombakinolar"
    },
    {
        "photo": "https://i.postimg.cc/example3.jpg",  # 3-reklama rasmi
        "text": "📢 <b>Premium kontent kanali!</b>\n\n🔥 Har kuni yangi postlar\n💰 Pullik kurslar bepul\n🎁 Sovg'alar va konkurslar",
        "button_text": "📢 A'zo bo'lish",
        "button_url": "t.me/Tarjimabombakinolar"
    }
]

# Hozirgi reklama indexi
current_ad_index = 0

# Obuna tekshirish funksiyasi
async def check_subscription(user_id: int) -> bool:
    """Foydalanuvchi barcha kanallarga obuna ekanligini tekshiradi"""
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ['left', 'kicked']:
                return False
        except Exception as e:
            logging.error(f"Obuna tekshirishda xatolik: {e}")
            return False
    return True

# Obuna tugmalarini yaratish
def get_subscription_keyboard():
    """Kanallar va tekshirish tugmasini yaratadi"""
    buttons = []
    for i, channel in enumerate(CHANNELS, 1):
        # Kanal nomini @ belgisiz ko'rsatish
        channel_name = channel.replace('@', '')
        buttons.append([types.InlineKeyboardButton(
            text=f"📢 {i}-Kanal", 
            url=f"https://t.me/{channel_name}"
        )])
    
    buttons.append([types.InlineKeyboardButton(
        text="✅ Tekshirish", 
        callback_data="check_subscription"
    )])
    
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)

# /start komandasi
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    
    # Admin uchun obuna tekshirishni o'tkazib yuborish
    if user_id == ADMIN_ID:
        first_name = message.from_user.first_name
        username = message.from_user.username or first_name
        await message.answer(
            f"👮 <b>Salom Admin {username}!</b>\n\n"
            f"🎬 <b>Epic kino kodini yuboring</b>\n"
            f"Masalan: <code>1</code>\n\n"
            f"Admin panel uchun: /admin",
            parse_mode="HTML"
        )
        return
    
    # Obuna tekshirish
    is_subscribed = await check_subscription(user_id)
    
    if not is_subscribed:
        await message.answer(
            "..👋 <b>Assalomu alaykum!</b>\n\n"
            "Botimizdan foydalanish uchun quyidagi kanallarga a'zo bo'ling:\n\n"
            "⬇️ Kanallarga obuna bo'lgandan so'ng <b>Tekshirish</b> tugmasini bosing",
            reply_markup=get_subscription_keyboard(),
            parse_mode="HTML"
        )
        return
    
    # Agar obuna bo'lsa
    first_name = message.from_user.first_name
    username = message.from_user.username or first_name
    
    await message.answer(
        f"👋 <b>Salom {username}!</b>\n\n"
        f"🤖 Botdan muvaffaqiyatli o'tdingiz! 🎉\n\n"
        f"🎬 <b>Kino kodini yuboring 🔢</b>\n"
        f"Masalan: <code>001</code>",
        parse_mode="HTML"
    )

# Tekshirish tugmasi bosilganda
@dp.callback_query(F.data == "check_subscription")
async def check_sub_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    
    # Obuna tekshirish
    is_subscribed = await check_subscription(user_id)
    
    if not is_subscribed:
        await callback.answer(
            "❌ Siz hali barcha kanallarga obuna bo'lmadingiz!\n"
            "Iltimos, hamma kanallarga obuna bo'ling.",
            show_alert=True
        )
        return
    
    # Agar obuna bo'lsa
    first_name = callback.from_user.first_name
    username = callback.from_user.username or first_name
    
    await callback.message.edit_text(
        f"👋 <b>salom {username}!</b>\n\n"
        f"🤖 Botdan muvaffaqiyatli o'tdingiz! 🎉\n\n"
        f"🎬 <b>Kino kino kodini yuboring 🔢</b>\n"
        f"Masalan: <code>001</code>",
        parse_mode="HTML"
    )
    await callback.answer("✅ Obuna tasdiqlandi!", show_alert=True)

# Admin paneli
@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Sizda admin huquqi yo'q!")
        return
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="➕ Kino qo'shish", callback_data="add_movie")],
        [types.InlineKeyboardButton(text="🗑 Kino o'chirish", callback_data="delete_movie")],
        [types.InlineKeyboardButton(text="📋 Barcha kinolar", callback_data="list_movies")]
    ])
    
    await message.answer(
        "👮 <b>Admin Panel</b>\n\n"
        "Quyidagi tugmalardan birini tanlang:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

# Kino qo'shish
@dp.callback_query(F.data == "add_movie")
async def add_movie_start(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    await callback.message.edit_text(
        "➕ <b>Kino qo'shish</b>\n\n"
        "Kino kodini yozing (masalan: 001):",
        parse_mode="HTML"
    )
    await state.set_state(AddMovie.waiting_for_code)
    await callback.answer()

@dp.message(AddMovie.waiting_for_code)
async def add_movie_code(message: types.Message, state: FSMContext):
    code = message.text.strip()
    
    if code in movies_db:
        await message.answer(f"⚠️ <code>{code}</code> kodi allaqachon mavjud!", parse_mode="HTML")
        return
    
    await state.update_data(code=code)
    await message.answer(
        f"✅ Kod saqlandi: <code>{code}</code>\n\n"
        "Endi kino faylini yuboring:",
        parse_mode="HTML"
    )
    await state.set_state(AddMovie.waiting_for_file)

@dp.message(AddMovie.waiting_for_file, F.video | F.document)
async def add_movie_file(message: types.Message, state: FSMContext):
    data = await state.get_data()
    code = data['code']
    
    # File ID ni saqlash
    if message.video:
        file_id = message.video.file_id
        file_type = "video"
    else:
        file_id = message.document.file_id
        file_type = "document"
    
    movies_db[code] = {
        "file_id": file_id,
        "file_type": file_type
    }
    save_data(movies_db)
    
    await message.answer(
        f"✅ Kino muvaffaqiyatli qo'shildi!\n\n"
        f"📝 Kod: <code>{code}</code>\n"
        f"📁 Fayl turi: {file_type}",
        parse_mode="HTML"
    )
    await state.clear()

# Kino o'chirish
@dp.callback_query(F.data == "delete_movie")
async def delete_movie_start(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    if not movies_db:
        await callback.message.edit_text("📭 Hozircha kinolar yo'q!")
        await callback.answer()
        return
    
    await callback.message.edit_text(
        "🗑 <b>Kino o'chirish</b>\n\n"
        "O'chirmoqchi bo'lgan kino kodini yozing:",
        parse_mode="HTML"
    )
    await state.set_state(DeleteMovie.waiting_for_code)
    await callback.answer()

@dp.message(DeleteMovie.waiting_for_code)
async def delete_movie_code(message: types.Message, state: FSMContext):
    code = message.text.strip()
    
    if code not in movies_db:
        await message.answer(f"❌ <code>{code}</code> kodi topilmadi!", parse_mode="HTML")
        return
    
    del movies_db[code]
    save_data(movies_db)
    
    await message.answer(
        f"✅ Kino o'chirildi!\n\n"
        f"📝 Kod: <code>{code}</code>",
        parse_mode="HTML"
    )
    await state.clear()

# Barcha kinolarni ko'rish
@dp.callback_query(F.data == "list_movies")
async def list_movies(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    if not movies_db:
        await callback.message.edit_text("📭 Hozircha kinolar yo'q!")
        await callback.answer()
        return
    
    text = "📋 <b>Barcha kinolar:</b>\n\n"
    for code in sorted(movies_db.keys()):
        text += f"📝 <code>{code}</code>\n"
    
    await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer()

# Foydalanuvchi kino kodini yozganda
@dp.message(F.text)
async def get_movie(message: types.Message):
    global current_ad_index
    user_id = message.from_user.id
    
    # Obuna tekshirish
    is_subscribed = await check_subscription(user_id)
    
    if not is_subscribed:
        await message.answer(
            "❌ Botdan foydalanish uchun kanallarga obuna bo'ling!",
            reply_markup=get_subscription_keyboard(),
            parse_mode="HTML"
        )
        return
    
    code = message.text.strip()
    
    if code not in movies_db:
        await message.answer(
            "❌ Bunday kino topilmadi!\n\n"
            "Kino qidirayotganda so'rovingiz faqat raqam bilan belgilansin (masalan: <code>1</code>)",
            parse_mode="HTML"
        )
        return
    
    movie = movies_db[code]
    
    try:
        if movie['file_type'] == "video":
            await message.answer_video(
                movie['file_id'],
                caption=f"🎬 Kod: <code>{code}</code>",
                parse_mode="HTML"
            )
        else:
            await message.answer_document(
                movie['file_id'],
                caption=f"🎬 Kod: <code>{code}</code>",
                parse_mode="HTML"
            )
        
        # Kino sonini sanash
        if user_id not in user_movie_count:
            user_movie_count[user_id] = 0
        
        user_movie_count[user_id] += 1
        
        # Har 3ta kinodan keyin reklama (navbat bilan)
        if user_movie_count[user_id] % 3 == 0:
            await asyncio.sleep(10)  # 1 soniya kutish
            
            # Hozirgi reklamani olish
            ad = REKLAMA_LIST[current_ad_index]
            
            # Reklama tugmasi
            ad_button = types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text=ad["button_text"], url=ad["button_url"])]
            ])
            
            # Reklama yuborish (rasm + matn + tugma)
            await message.answer_photo(
                photo=ad["photo"],
                caption=ad["text"],
                reply_markup=ad_button,
                parse_mode="HTML"
            )
            
            # Keyingi reklamaga o'tish (navbat)
            current_ad_index = (current_ad_index + 1) % len(REKLAMA_LIST)
    
    except Exception as e:
        logging.error(f"Xatolik: {e}")
        await message.answer("salom bot foyalanuvchilari !")

# Botni ishga tushirish
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    print("🤖 Bot ishga tushdi...")
    asyncio.run(main())