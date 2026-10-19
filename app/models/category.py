from app.db.base import Base
from sqlalchemy import Integer, String, ForeignKey, func, DateTime, UniqueConstraint
from datetime import datetime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from enum import StrEnum
from sqlalchemy import Enum as SQLEnum

class CategoryType(StrEnum):
    INCOME = 'income'
    EXPENSE = 'expense'

class Category(Base):

    __tablename__ = 'categories'

    __table_args__ = (
        UniqueConstraint('user_id', 'name', 'type', name='uq_category_user_name_type'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    type: Mapped[CategoryType] = mapped_column(
        SQLEnum(CategoryType, native_enum=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())