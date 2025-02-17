from typing import List
import enum
from sqlalchemy import ForeignKey, String, Table, Column, Enum, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, declared_attr

class Base(DeclarativeBase):
    pass


# Association table for the many-to-many relationship
pulsar_user = Table(
    "pulsar_user",
    Base.metadata,
    Column("pulsar_id", ForeignKey("pulsars.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
)

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    pulsars: Mapped[List["Pulsar"]] = relationship(
        secondary=pulsar_user,
        back_populates="users",
        cascade="all, delete",
    )

    def __repr__(self):
        return f"<User {self.email}>"

class Pulsar(Base):
    __tablename__ = "pulsars"
    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(255))
    api_key: Mapped[str] = mapped_column(String(255))
    users: Mapped[List[User]] = relationship(
        secondary=pulsar_user,
        back_populates="pulsars",
        cascade="all, delete",
    )

    def __repr__(self):
        return f"<Pulsar {self.url}>"

class Message(enum.Enum):
    CREATED = "CREATED"
    UPDATED = "UPDATED"
    DELETED = "DELETED"

class Outbox(Base):
    __tablename__ = "outbox"
    id: Mapped[int] = mapped_column(primary_key=True)
    message: Mapped[Message] = mapped_column(Enum(Message))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    pulsar_id: Mapped[int] = mapped_column(ForeignKey("pulsars.id", ondelete="CASCADE"))
    deleted_at: Mapped[DateTime] = mapped_column(DateTime)


    def __repr__(self):
        return f"<Outbox {self.message}>"
