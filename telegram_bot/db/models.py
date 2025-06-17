from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
    )

    password = Column(
        String(128),
        nullable=False,
    )
    last_login = Column(
        DateTime,
        nullable=True,
    )
    is_superuser = Column(
        Boolean,
        default=False,
        nullable=False,
    )
    first_name = Column(
        String(150),
        nullable=False,
    )
    last_name = Column(
        String(150),
        nullable=False,
    )
    email = Column(
        String(254),
        unique=True,
        nullable=False,
    )
    is_staff = Column(
        Boolean,
        default=False,
        nullable=False,
    )
    is_active = Column(
        Boolean,
        default=False,
        nullable=False,
    )
    date_joined = Column(
        DateTime,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        nullable=False,
    )
    updated_at = Column(
        DateTime,
        nullable=False,
    )
    is_deleted = Column(
        Boolean,
        default=False,
        nullable=False,
    )
    deleted_at = Column(
        DateTime,
        nullable=True,
    )

    telegram_id = Column(
        BigInteger,
        unique=True,
        nullable=True,
    )
    phone = Column(
        String(20),
        nullable=True,
    )

    def __repr__(self):
        return f"<User(id='{self.id}', email='{self.email}', " f"phone='{self.phone}', telegram_id={self.telegram_id})>"
