from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base, MilestonesAware

if TYPE_CHECKING:
    from app.models.checks import Check


class User(Base, MilestonesAware):
    __tablename__ = 'users'
    name: Mapped[str] = mapped_column(String(512), nullable=False)
    login: Mapped[str] = mapped_column(String(512), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(512), nullable=False)
    password: Mapped[str] = mapped_column(String(512), nullable=False)

    checks: Mapped[list['Check']] = relationship('Check', back_populates='creator', lazy='selectin')
