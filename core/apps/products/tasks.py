from celery import shared_task
from django.conf import settings
import logging
import requests

logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/"


@shared_task
def send_order_creation_telegram_message(telegram_id: int):
    try:
        message_text = "✅ Ваш заказ успешно создан!"

        # Удаляем parse_mode
        payload = {"chat_id": telegram_id, "text": message_text}

        response = requests.post(TELEGRAM_API_URL + "sendMessage", json=payload)
        response.raise_for_status()

        response_data = response.json()
        if response_data.get("ok"):
            logger.info(f"Сообщение об успешном создании заказа отправлено пользователю {telegram_id}.")
        else:
            logger.error(
                f"Telegram API вернул ошибку для {telegram_id}: {response_data.get('description', 'Неизвестная ошибка')}"
            )

    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка HTTP-запроса при отправке сообщения пользователю {telegram_id}: {e}")
    except Exception as e:
        logger.error(f"Непредвиденная ошибка при отправке сообщения пользователю {telegram_id}: {e}")
