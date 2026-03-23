import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(',')))

# ID каналов/чатов для логов (опционально)
LOG_CHANNEL_ID = None  # Укажите ID канала для логов, если нужно

# Роли
ROLES = {
    "recruit": "Новичок",
    "member": "Боец",
    "elite": "Элита",
    "vice": "Вице-лидер",
    "leader": "Лидер"
}

# Права доступа (какая роль что может)
PERMISSIONS = {
    "invite": ["vice", "leader"],  # Кто может выдавать инвайты
    "kick": ["vice", "leader"],    # Кто может кикать
    "warn": ["vice", "leader"],    # Кто может выдавать варны
    "full": ["vice", "leader"],    # Кто может выдавать фул (оружие и т.д.)
    "admin_panel": ["leader"]      # Доступ к админке
}

# Ранги (1-10)
RANKS = [str(i) for i in range(1, 11)]

# Доступные машины по рангам
CARS_BY_RANK = {
    "1": ["Faggio", "Blista"],
    "2": ["Sultan", "Elegy"],
    "3": ["Jester", "Massacro"],
    "4": ["Zentorno", "Turismo R"],
    "5": ["Entity XF", "Cheetah"],
    "6": ["Osiris", "T20"],
    "7": ["Reaper", "FMJ"],
    "8": ["X80 Proto", "ETR1"],
    "9": ["Nero", "Tempesta"],
    "10": ["RE-7B", "811", "Itali GTB"]
}

# Максимальное количество варнов до кика
MAX_WARNS = 3