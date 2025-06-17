import asyncio
import inspect
import logging
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
)

from sqlalchemy.ext.asyncio import AsyncSession

from aiogram import (
    Bot,
    Dispatcher,
    types,
)
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web
from punq import Container
from telegram_bot.config import (
    BOT_WEB_SERVER_PORT,
    TELEGRAM_BOT_TOKEN,
)
from telegram_bot.db.session import AsyncSessionLocal
from telegram_bot.handlers.user_handlers import register_user_handlers
from telegram_bot.web_server import init_web_server


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")


class PunqMiddleware:
    def __init__(self, container: Container):
        self.container = container

    async def __call__(
        self,
        handler: Callable[[types.TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: types.TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async with AsyncSessionLocal() as session:
            data["db_session"] = session

            signature = inspect.signature(handler)
            for param_name, param in signature.parameters.items():
                if (
                    param_name not in data
                    and param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
                    and param.annotation != inspect.Parameter.empty
                ):

                    if param.annotation is AsyncSession:
                        continue

                    try:
                        resolved_dependency = self.container.resolve(param.annotation)
                        data[param_name] = resolved_dependency
                    except Exception as e:
                        logging.warning(
                            f"Could not resolve dependency '{param_name}' of type '{param.annotation}' from Punq container: {e}"
                        )
                        pass

            return await handler(event, data)


def configure_punq_container() -> Container:
    container = Container()
    return container


async def main():
    container = configure_punq_container()

    bot = Bot(token=TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode="MarkdownV2"))
    storage = MemoryStorage()

    dp = Dispatcher(storage=storage)
    dp["punq_container"] = container

    dp.update.middleware.register(PunqMiddleware(container))

    register_user_handlers(dp)

    web_app = init_web_server(bot)
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", BOT_WEB_SERVER_PORT)
    web_server_task = asyncio.create_task(site.start())

    logging.info("Starting bot polling...")
    bot_polling_task = asyncio.create_task(dp.start_polling(bot))

    await asyncio.gather(web_server_task, bot_polling_task)


if __name__ == "__main__":
    try:
        logging.info("Bot application initiated.")
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot stopped by KeyboardInterrupt.")
    except Exception as e:
        logging.exception(f"An unexpected error occurred during bot startup: {e}")
