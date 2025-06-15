import asyncio
from celery import shared_task
from telegram import Bot
from telegram.error import TelegramError
from django.conf import settings

from core.apps.user.models import User

TELEGRAM_BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN


@shared_task
def send_order_creation_telegram_message(user: User):

    telegram_id = user.telegram_id

    async def _send_message():
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        try:
            message_text = "✅ Ваш заказ успешно создан!"
            await bot.send_message(chat_id=telegram_id, text=message_text)

        except TelegramError as e:
            print(f"Ошибка при отправке сообщения об успешном создании заказа пользователю {telegram_id}: {e}")
        finally:
            await bot.close()

    asyncio.run(_send_message())
