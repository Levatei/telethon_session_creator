"""
Полная авторизация Telethon — запрос кода + вход + сохранение сессии
Запускать один раз для создания авторизованной сессии
"""

import asyncio
import re
import sys
from pathlib import Path

from telethon import TelegramClient
from telethon.errors import (
    SessionPasswordNeededError,
    PhoneCodeInvalidError,
    PhoneCodeExpiredError,
)

SESSION_DIR = Path(__file__).resolve().parent / "session"

APP_ID = 12345678 # берётся из my.telegram.org или публичный
APP_HASH = "" # берётся из my.telegram.org или публичный
DEVICE_MODEL = "Windows 11 x64"
SYSTEM_VERSION = "Satellite C660"
APP_VERSION = "6.5.1 x64"
LANG_CODE = "en"
SYSTEM_LANG_CODE = "en-US"


def norm_phone(s: str) -> str:
    d = re.sub(r"\D", "", s)
    return "+" + d if d else s


async def full_auth(phone: str, proxy=None):
    phone = norm_phone(phone)
    if not re.fullmatch(r"\+\d+", phone):
        print("Неверный формат телефона")
        return False

    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    # Сессия сохранится как session/<номер_телефона>.session
    session_path = SESSION_DIR / re.sub(r"\D", "", phone)

    client = TelegramClient(
        str(session_path),
        APP_ID,
        APP_HASH,
        proxy=proxy,
        device_model=DEVICE_MODEL,
        system_version=SYSTEM_VERSION,
        app_version=APP_VERSION,
        lang_code=LANG_CODE,
        system_lang_code=SYSTEM_LANG_CODE,
    )

    await client.connect()

    # Если уже авторизован — выходим
    if await client.is_user_authorized():
        me = await client.get_me()
        print(f"Уже авторизован как: {me.first_name} (@{me.username})")
        await client.disconnect()
        return True

    # Запрашиваем код
    print(f"Запрашиваем код для {phone}...")
    sent = await client.send_code_request(phone)
    print("Код отправлен! Проверьте Telegram.")

    # Получаем код от пользователя
    code = input("Введите код из Telegram: ").strip()

    try:
        me = await client.sign_in(phone, code, phone_code_hash=sent.phone_code_hash)
        print(f"\n✅ Авторизован успешно: {me.first_name} (@{me.username})")
        print(f"   Сессия сохранена: {session_path}.session")
        await client.disconnect()
        return True

    except PhoneCodeInvalidError:
        print("❌ Неверный код. Попробуйте ещё раз.")
        await client.disconnect()
        return False

    except PhoneCodeExpiredError:
        print("❌ Код истёк. Запустите скрипт заново.")
        await client.disconnect()
        return False

    except SessionPasswordNeededError:
        # Двухфакторная аутентификация
        print("🔒 Включена двухфакторная аутентификация (2FA)")
        password = input("Введите пароль 2FA: ").strip()
        try:
            me = await client.sign_in(password=password)
            print(f"\n✅ Авторизован успешно (2FA): {me.first_name} (@{me.username})")
            print(f"   Сессия сохранена: {session_path}.session")
            await client.disconnect()
            return True
        except Exception as e:
            print(f"❌ Ошибка 2FA: {e}")
            await client.disconnect()
            return False

    except Exception as e:
        print(f"❌ Ошибка при входе: {e}")
        await client.disconnect()
        return False


if __name__ == "__main__":
    phone = sys.argv[1].strip() if len(sys.argv) > 1 else input("Телефон (с кодом страны, напр. +79001234567): ").strip()
    if not phone:
        sys.exit(1)

    ok = asyncio.run(full_auth(phone))
    if ok:
        print("\n👉 Теперь укажите путь к сессии в pump_monitor.py:")
        digits = re.sub(r"\D", "", phone)
        print(f"   SESSION_NAME = 'session/{digits}'")
    sys.exit(0 if ok else 1)