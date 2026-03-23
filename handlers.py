import asyncio
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text

from config import *
import db
from keyboards import *


# Состояния для FSM
class AdminStates(StatesGroup):
    waiting_for_user = State()
    waiting_for_full = State()
    waiting_for_rank = State()
    waiting_for_role = State()


# Проверка прав
def has_permission(user_id, action):
    user = db.get_user(user_id)
    if not user:
        return False
    role = user[2]
    return role in PERMISSIONS.get(action, [])


# Старт / команды
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    db.add_user(user_id, username)

    # Проверка на приглашение (если перешли по ссылке)
    args = message.get_args()
    if args and args.isdigit():
        inviter_id = int(args)
        db.update_user_field(user_id, "invited_by", inviter_id)
        await message.answer(f"✅ Вы были приглашены в семью {inviter_id}!")

    await message.answer(
        f"Добро пожаловать в Majestic Family, {username}!\n"
        f"Используйте кнопки для навигации.",
        reply_markup=main_menu()
    )


async def cmd_profile(message: types.Message):
    user = db.get_user(message.from_user.id)
    if not user:
        await message.answer("Ошибка: пользователь не найден.")
        return

    caps = db.get_caps_count(user[0])
    role_name = ROLES.get(user[2], user[2])

    text = (
        f"👤 *Профиль игрока*\n"
        f"ID: `{user[0]}`\n"
        f"Имя: @{user[1]}\n"
        f"Роль: {role_name}\n"
        f"Ранг: {user[4]}\n"
        f"Варны: {user[3]}/{MAX_WARNS}\n"
        f"Капты (Атака): {caps['attack']}\n"
        f"Капты (Защита): {caps['defense']}\n"
        f"Выданный фул: {user[5] or 'Нет'}"
    )
    await message.answer(text, parse_mode="Markdown")


async def cmd_my_cars(message: types.Message):
    user = db.get_user(message.from_user.id)
    if not user:
        return
    cars = user[6]
    rank = str(user[4])
    available = ", ".join(CARS_BY_RANK.get(rank, []))
    text = f"🚗 *Ваши машины:*\n{cars or 'Нет машин'}\n\nДоступно для ранга {rank}: {available}"
    await message.answer(text, parse_mode="Markdown")


# Инлайн колбэки
async def callback_profile(call: types.CallbackQuery):
    await cmd_profile(call.message)
    await call.answer()


async def callback_my_cars(call: types.CallbackQuery):
    await cmd_my_cars(call.message)
    await call.answer()


async def callback_caps_menu(call: types.CallbackQuery):
    await call.message.edit_reply_markup(reply_markup=caps_menu())
    await call.answer()


async def callback_back_main(call: types.CallbackQuery):
    await call.message.edit_reply_markup(reply_markup=main_menu())
    await call.answer()


async def callback_cap(call: types.CallbackQuery):
    cap_type = "attack" if "attack" in call.data else "defense"
    user_id = call.from_user.id
    db.add_cap(user_id, cap_type)
    caps = db.get_caps_count(user_id)
    await call.answer(f"✅ Капт ({cap_type}) засчитан! Всего: Атака {caps['attack']}, Защита {caps['defense']}",
                      show_alert=True)
    await call.message.edit_reply_markup(reply_markup=caps_menu())


# Админка
async def callback_admin_panel(call: types.CallbackQuery):
    if not has_permission(call.from_user.id, "admin_panel"):
        await call.answer("⛔ Нет прав", show_alert=True)
        return
    await call.message.answer("🔧 Админ-панель:", reply_markup=admin_panel())
    await call.answer()


async def admin_invite(call: types.CallbackQuery, state: FSMContext):
    if not has_permission(call.from_user.id, "invite"):
        await call.answer("⛔ Нет прав", show_alert=True)
        return
    await call.message.answer("Введите ID или username пользователя, которому выдать инвайт:")
    await state.set_state(AdminStates.waiting_for_user)
    await state.update_data(action="invite")
    await call.answer()


async def admin_warn(call: types.CallbackQuery, state: FSMContext):
    if not has_permission(call.from_user.id, "warn"):
        await call.answer("⛔ Нет прав", show_alert=True)
        return
    await call.message.answer("Введите ID или username пользователя для выдачи варна:")
    await state.set_state(AdminStates.waiting_for_user)
    await state.update_data(action="warn")
    await call.answer()


async def admin_kick(call: types.CallbackQuery, state: FSMContext):
    if not has_permission(call.from_user.id, "kick"):
        await call.answer("⛔ Нет прав", show_alert=True)
        return
    await call.message.answer("Введите ID или username пользователя для кика:")
    await state.set_state(AdminStates.waiting_for_user)
    await state.update_data(action="kick")
    await call.answer()


async def admin_full(call: types.CallbackQuery, state: FSMContext):
    if not has_permission(call.from_user.id, "full"):
        await call.answer("⛔ Нет прав", show_alert=True)
        return
    await call.message.answer(
        "Введите ID пользователя и список выданного фула (оружие, броня, паттерны) через запятую:\nПример: `123456789, AK-47, Броня, Камуфляж`")
    await state.set_state(AdminStates.waiting_for_full)
    await call.answer()


async def process_full_input(message: types.Message, state: FSMContext):
    data = message.text.split(',')
    if len(data) < 2:
        await message.answer("Неверный формат. Используйте: ID, предмет1, предмет2...")
        return
    target_id = int(data[0].strip())
    full_items = ', '.join([x.strip() for x in data[1:]])
    db.update_user_field(target_id, "full_given", full_items)
    await message.answer(f"✅ Фул выдан пользователю {target_id}: {full_items}")
    await state.finish()


async def process_admin_input(message: types.Message, state: FSMContext):
    data = await state.get_data()
    action = data.get("action")
    target = message.text.strip()

    # Поиск пользователя (по username или ID)
    user_id = None
    if target.isdigit():
        user_id = int(target)
    else:
        # Поиск по username (упрощенно)
        all_users = db.get_all_users()  # Нужно добавить эту функцию в db
        for u in all_users:
            if u[1] == target:
                user_id = u[0]
                break

    if not user_id:
        await message.answer("Пользователь не найден.")
        await state.finish()
        return

    if action == "invite":
        # Генерация ссылки-приглашения
        bot_info = await message.bot.get_me()
        link = f"https://t.me/{bot_info.username}?start={user_id}"
        await message.answer(f"🔗 Ссылка для приглашения: {link}")

    elif action == "warn":
        warns = db.add_warn(user_id)
        if warns >= MAX_WARNS:
            # Кикаем (удаляем из БД)
            db.delete_user(user_id)  # Нужно добавить функцию
            await message.answer(f"⚠️ Пользователь {user_id} получил {warns}/{MAX_WARNS} варнов и был кикнут.")
        else:
            await message.answer(f"⚠️ Пользователю {user_id} выдан варн. Теперь варнов: {warns}/{MAX_WARNS}")

    elif action == "kick":
        db.delete_user(user_id)
        await message.answer(f"👢 Пользователь {user_id} кикнут из семьи.")

    await state.finish()


# Регистрация хендлеров
def register_handlers(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands=['start'])
    dp.register_message_handler(cmd_profile, commands=['profile'])
    dp.register_message_handler(cmd_my_cars, commands=['mycars'])

    dp.register_callback_query_handler(callback_profile, text="profile")
    dp.register_callback_query_handler(callback_my_cars, text="my_cars")
    dp.register_callback_query_handler(callback_caps_menu, text="caps_menu")
    dp.register_callback_query_handler(callback_back_main, text="back_main")
    dp.register_callback_query_handler(callback_cap, Text(startswith="cap_"))
    dp.register_callback_query_handler(callback_admin_panel, text="admin_panel")
    dp.register_callback_query_handler(admin_invite, text="admin_invite")
    dp.register_callback_query_handler(admin_warn, text="admin_warn")
    dp.register_callback_query_handler(admin_kick, text="admin_kick")
    dp.register_callback_query_handler(admin_full, text="admin_full")

    dp.register_message_handler(process_full_input, state=AdminStates.waiting_for_full)
    dp.register_message_handler(process_admin_input, state=AdminStates.waiting_for_user)