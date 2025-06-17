from aiohttp import web
from telegram_bot.config import BOT_WEB_SERVER_SECRET_KEY


_aiogram_bot = None


async def handle_notify_user(request: web.Request):
    if _aiogram_bot is None:
        return web.json_response({"status": "error", "message": "Bot not initialized"}, status=500)

    if request.method != "POST":
        return web.json_response({"status": "error", "message": "Method Not Allowed"}, status=405)

    try:
        data = await request.json()
    except Exception:
        return web.json_response({"status": "error", "message": "Invalid JSON format"}, status=400)

    received_secret_key = data.get("secret_key")
    if received_secret_key != BOT_WEB_SERVER_SECRET_KEY:
        return web.json_response({"status": "error", "message": "Unauthorized"}, status=403)

    telegram_id = data.get("telegram_id")
    message_text = data.get("message_text")

    if not all([telegram_id, message_text]):
        return web.json_response({"status": "error", "message": "Missing 'telegram_id' or 'message_text'"}, status=400)

    try:
        telegram_id = int(telegram_id)
    except ValueError:
        return web.json_response({"status": "error", "message": "Invalid 'telegram_id' format"}, status=400)

    try:
        await _aiogram_bot.send_message(chat_id=telegram_id, text=message_text, parse_mode="MarkdownV2")
        return web.json_response({"status": "success", "message": "Notification sent"}, status=200)
    except Exception as e:
        return web.json_response({"status": "error", "message": f"Failed to send notification: {e}"}, status=500)


def init_web_server(aiogram_bot_instance) -> web.Application:
    global _aiogram_bot
    _aiogram_bot = aiogram_bot_instance

    app = web.Application()
    app.router.add_post("/notify_user", handle_notify_user)
    return app
