from app.db.base import Base
from sqlalchemy import Integer, String, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import relationship, mapped_column, Mapped
from datetime import datetime


class User(Base):

    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    categories: Mapped[list['Category']] = relationship(back_populates='user', cascade='all, delete-orphan')
    transactions: Mapped[list['Transaction']] = relationship(back_populates='user', cascade='all, delete-orphan')