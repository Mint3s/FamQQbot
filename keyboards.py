from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📊 Мой профиль", callback_data="profile"),
        InlineKeyboardButton("🚗 Мои машины", callback_data="my_cars"),
        InlineKeyboardButton("🎯 Капты", callback_data="caps_menu")
    )
    return kb

def caps_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🏆 Взять капт (Атака)", callback_data="cap_attack"),
        InlineKeyboardButton("🛡 Взять капт (Защита)", callback_data="cap_defense"),
        InlineKeyboardButton("◀️ Назад", callback_data="back_main")
    )
    return kb

def admin_panel():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("➕ Выдать инвайт", callback_data="admin_invite"),
        InlineKeyboardButton("⚠️ Выдать варн", callback_data="admin_warn"),
        InlineKeyboardButton("🔫 Выдать фул", callback_data="admin_full"),
        InlineKeyboardButton("👢 Кикнуть игрока", callback_data="admin_kick"),
        InlineKeyboardButton("📈 Повысить ранг", callback_data="admin_up_rank"),
        InlineKeyboardButton("📉 Понизить ранг", callback_data="admin_down_rank"),
        InlineKeyboardButton("🏅 Сменить роль", callback_data="admin_change_role"),
        InlineKeyboardButton("◀️ Закрыть", callback_data="close_admin")
    )
    return kb