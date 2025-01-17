from typing import List
from sqlalchemy import ForeignKey, String, Table, Column
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

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
