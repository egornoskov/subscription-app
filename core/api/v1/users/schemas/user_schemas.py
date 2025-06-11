from typing import Optional

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
)


class UserCreateIn(BaseModel):
    email: EmailStr = Field(
        ...,
        description="Email пользователя",
    )
    password: str = Field(
        ...,
        min_length=8,
        description="Пароль пользователя (минимум 8 символов)",
    )
    first_name: str = Field(
        ...,
        min_length=2,
        description="Имя пользователя",
    )
    last_name: str = Field(
        ...,
        min_length=2,
        description="Фамилия пользователя",
    )
    phone: str = Field(
        ...,
        pattern=r"^\+?1?\d{9,15}$",
        description="Телефон пользователя только цифры, должен начинаться с +",
    )


class UserUpdateIn(BaseModel):
    email: Optional[EmailStr] = Field(
        None,
        description="Новый email пользователя",
    )
    password: Optional[str] = Field(
        None,
        min_length=8,
        description="Новый пароль пользователя (минимум 8 символов)",
    )
    first_name: Optional[str] = Field(
        None,
        min_length=2,
        description="Новое имя пользователя",
    )
    last_name: Optional[str] = Field(None, min_length=2, description="Новая фамилия пользователя")
    phone: Optional[str] = Field(
        None,
        pattern=r"^\+?1?\d{9,15}$",
        description="Новый телефон пользователя (только цифры, может начинаться с +)",
    )

    def validate_for_put(self):
        required_fields_for_put = ["email", "password", "first_name", "last_name", "phone"]
        missing_fields = [field for field in required_fields_for_put if getattr(self, field) is None]
        if missing_fields:
            raise ValueError(
                f"Для полного обновления (PUT) необходимы все поля: {', '.join(missing_fields)}",
            )
