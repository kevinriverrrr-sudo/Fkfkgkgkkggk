# Telegram bot (safe template)

Этот бот:
- принимает номер телефона через стандартную кнопку Telegram `request_contact`;
- выполняет только проверку доступности `https://x5id.ru` через `requests`;
- **не** автоматизирует вход, отправку/подбор SMS-кодов и доступ к чужим аккаунтам.

## Запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export TELEGRAM_BOT_TOKEN="<ваш_токен>"
python bot.py
```

## Почему так

Автоматизация входа на сторонние сервисы и «чекер» аккаунтов может нарушать правила сервиса и закон. Этот пример оставляет только легальный безопасный сценарий.
