from datetime import datetime
import typing as t
from sqlalchemy import Boolean, Column, Integer, String, Enum, DateTime, func, ForeignKey
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import Mapped, mapped_column, relationship

class_registry: t.Dict = {}


@as_declarative(class_registry=class_registry)
class Base:
    id: t.Any
    __name__: str

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class Users(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(50), unique=True)
    is_active: Mapped[str] = mapped_column(Boolean, default=False)
    password: Mapped[str] = mapped_column(String(255))

    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    todos: Mapped[list['Todo']] = relationship(back_populates='author', lazy='selectin')


class Todo(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    complete: Mapped[bool] = mapped_column(Boolean, default=False)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    author: Mapped['Users'] = relationship(back_populates='todos')
