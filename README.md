# telethon_session_creator

Скрипт для одноразовой авторизации [Telethon](https://docs.telethon.dev/): запрос кода, вход, сохранение `.session` в папку `session/`.

## Зависимости

```bash
pip install telethon
```

## API ID и API Hash

В `auth.py` укажите `APP_ID` и `APP_HASH`.

Публичные **api_id** и **api_hash** можно взять здесь:  
[Sunrise Protocol — публичные приложения Telegram](https://sunrise-protocol.com/threads/app-hash-app-id-publichnyx-prilozhenij-telegram-speshl-fo-telegram-prime.147/)

Альтернатива: [my.telegram.org](https://my.telegram.org) (свой проект приложения).

## Запуск

```bash
python auth.py +79001234567
```

Либо без аргумента — скрипт спросит номер. После успешного входа файл сессии будет в `session/<цифры_номера>.session`.

## Безопасность

Не публикуйте сессии и секреты. `APP_HASH` в репозитории держите только как плейсхолдер или используйте переменные окружения при необходимости.
