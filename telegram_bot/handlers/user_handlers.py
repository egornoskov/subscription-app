import logging
import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from aiogram import (
    F,
    Router,
    types,
)
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import (
    State,
    StatesGroup,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from telegram_bot.db.models import User


logger = logging.getLogger(__name__)


def escape_markdown_v2(text: str) -> str:
    special_chars = r"_*[]()~`>#+-=|{}.!"
    for char in special_chars:
        text = text.replace(char, f"\\{char}")
    return text


def normalize_phone_number(phone_number_str: str) -> str:
    if not phone_number_str:
        return ""

    cleaned_number = re.sub(r"\D", "", phone_number_str)

    if cleaned_number.startswith("8") and len(cleaned_number) == 11:
        cleaned_number = "7" + cleaned_number[1:]

    if not cleaned_number.startswith("+"):
        return "+" + cleaned_number

    return cleaned_number


class UserActivationStates(StatesGroup):
    waiting_for_phone = State()


user_router = Router()


@user_router.message(CommandStart())
async def command_start_handler(message: types.Message, state: FSMContext) -> None:
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(text="Поделиться номером телефона", request_contact=True)

    await message.answer(
        "Для активации аккаунта, пожалуйста, поделитесь своим номером телефона "
        "\\(только номера, начинающиеся с '\\+'\\)\\.",
        reply_markup=keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True),
        parse_mode="MarkdownV2",
    )

    await state.set_state(UserActivationStates.waiting_for_phone)


@user_router.message(F.contact, UserActivationStates.waiting_for_phone)
async def process_phone_by_contact_button(message: types.Message, state: FSMContext, db_session: AsyncSession) -> None:
    phone_number_raw = message.contact.phone_number
    phone_number_normalized = normalize_phone_number(phone_number_raw)
    telegram_id = message.from_user.id

    escaped_phone_number = escape_markdown_v2(phone_number_normalized)
    await message.answer(
        f"Спасибо, ваш номер: `{escaped_phone_number}`\\. Пытаюсь активировать аккаунт\\.\\.\\.",
        parse_mode="MarkdownV2",
    )

    await _process_activation(message, state, phone_number_normalized, telegram_id, db_session)


@user_router.message(
    F.text.regexp(r"^(?:\+)?[\d\s\-()]{7,20}$"),
    UserActivationStates.waiting_for_phone,
)
async def process_phone_by_text(message: types.Message, state: FSMContext, db_session: AsyncSession) -> None:
    phone_number_raw = message.text
    phone_number_normalized = normalize_phone_number(phone_number_raw)
    telegram_id = message.from_user.id

    escaped_phone_number = escape_markdown_v2(phone_number_normalized)
    await message.answer(
        f"Спасибо, ваш номер: `{escaped_phone_number}`\\. Пытаюсь активировать аккаунт\\.\\.\\.",
        parse_mode="MarkdownV2",
    )

    await _process_activation(message, state, phone_number_normalized, telegram_id, db_session)


@user_router.message(
    ~F.contact & ~F.text.regexp(r"^(?:\+)?[\d\s\-()]{7,20}$"),
    UserActivationStates.waiting_for_phone,
)
async def process_invalid_phone(message: types.Message, state: FSMContext) -> None:
    await message.answer(
        "Это не похоже на номер телефона\\. Пожалуйста, поделитесь своим номером "
        "через кнопку ниже, или введите его в формате `+79XXXXXXXXX`\\.",
        parse_mode="MarkdownV2",
    )


async def _process_activation(
    message: types.Message,
    state: FSMContext,
    phone_number: str,
    telegram_id: int,
    db_session: AsyncSession,
) -> None:
    try:
        stmt = select(User).where(User.phone == phone_number)
        result = await db_session.execute(stmt)
        user = result.scalars().first()

        if user is None:
            await message.answer(
                "Пользователь с таким номером телефона не найден в системе\\. "
                "Пожалуйста, проверьте номер или свяжитесь с поддержкой\\.",
                reply_markup=types.ReplyKeyboardRemove(),
                parse_mode="MarkdownV2",
            )
            return
        if user.telegram_id and user.telegram_id != telegram_id:
            await message.answer(
                "Этот номер телефона уже привязан к другому Telegram аккаунту\\. "
                "Пожалуйста, свяжитесь с поддержкой, если считаете, что это ошибка\\.",
                reply_markup=types.ReplyKeyboardRemove(),
                parse_mode="MarkdownV2",
            )
            return

        was_inactive = not user.is_active
        user.telegram_id = telegram_id
        if was_inactive:
            user.is_active = True

        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        if was_inactive:
            await message.answer(
                "Ваш аккаунт успешно активирован и привязан к Telegram\\!",
                reply_markup=types.ReplyKeyboardRemove(),
                parse_mode="MarkdownV2",
            )
        else:
            await message.answer(
                "Ваш аккаунт уже был активен, Telegram ID обновлен\\.",
                reply_markup=types.ReplyKeyboardRemove(),
                parse_mode="MarkdownV2",
            )

    except Exception as e:
        await db_session.rollback()
        logger.error(f"Error processing user activation with SQLAlchemy: {e}", exc_info=True)
        await message.answer(
            "Произошла непредвиденная ошибка при активации аккаунта\\. Пожалуйста, попробуйте позже\\.",
            reply_markup=types.ReplyKeyboardRemove(),
            parse_mode="MarkdownV2",
        )
    finally:
        await state.clear()


def register_user_handlers(dp: Router) -> None:
    dp.include_router(user_router)
