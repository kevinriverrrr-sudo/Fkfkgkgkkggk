import logging
import os
from dataclasses import dataclass

import requests
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

ASK_CONTACT = 1


@dataclass
class X5Status:
    reachable: bool
    status_code: int | None
    message: str


def check_x5_health(timeout: int = 10) -> X5Status:
    """Checks if the public X5 ID page is reachable.

    The bot does not automate login/SMS or access third-party accounts.
    """
    url = "https://x5id.ru"
    try:
        response = requests.get(url, timeout=timeout)
        return X5Status(
            reachable=response.ok,
            status_code=response.status_code,
            message="Сайт доступен" if response.ok else "Сайт ответил с ошибкой",
        )
    except requests.RequestException as exc:
        logger.warning("X5 check failed: %s", exc)
        return X5Status(reachable=False, status_code=None, message="Сайт недоступен")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [[KeyboardButton("Отправить номер", request_contact=True)]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

    await update.message.reply_text(
        "Привет! Отправьте ваш номер через кнопку ниже.\n\n"
        "Важно: бот не выполняет автоматический вход на сторонние аккаунты и не запрашивает SMS-коды за вас.",
        reply_markup=markup,
    )
    return ASK_CONTACT


async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    contact = update.message.contact
    if contact is None:
        await update.message.reply_text("Пожалуйста, используйте кнопку «Отправить номер».")
        return ASK_CONTACT

    context.user_data["phone"] = contact.phone_number
    x5_status = check_x5_health()

    status_line = (
        f"Проверка x5id.ru: {x5_status.message}"
        + (f" (HTTP {x5_status.status_code})" if x5_status.status_code else "")
    )

    await update.message.reply_text(
        "Номер получен: "
        f"{contact.phone_number}\n"
        f"{status_line}\n\n"
        "Дальше вы можете вручную войти в официальный сервис X5 ID в своем браузере."
        "\nЕсли нужен легальный бот для напоминаний/уведомлений — помогу добавить.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Ок, отменено.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("Set TELEGRAM_BOT_TOKEN environment variable")

    application = Application.builder().token(token).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_CONTACT: [MessageHandler(filters.CONTACT, handle_contact)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
