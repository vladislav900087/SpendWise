from app.db.base import Base
from sqlalchemy import Integer, ForeignKey, String, Numeric, CheckConstraint, DateTime, func, Date
from sqlalchemy.orm import relationship, mapped_column, Mapped
from datetime import datetime, date
from decimal import Decimal
from enum import StrEnum
from sqlalchemy import Enum as SQLEnum




class TransactionType(StrEnum):
    INCOME = 'income'
    EXPENSE = 'expense'


class Transaction(Base):

    __tablename__ = 'transactions'

    __table_args__ = (CheckConstraint('amount > 0', name='ck_transaction_amount_positive'),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id', ondelete='RESTRICT'), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default='USD')
    type: Mapped[TransactionType] = mapped_column(SQLEnum(TransactionType, native_enum=False, values_callable=lambda x: [e.value for e in x]), nullable=False, default=TransactionType.INCOME.value)
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False, index=True, default=date.today())
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    user: Mapped['User'] = relationship(back_populates='transactions')
    category: Mapped['Category'] = relationship(back_populates='transactions')





