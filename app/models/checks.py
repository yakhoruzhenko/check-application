from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

from sqlalchemy import ForeignKey, Index, String, event, text
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Mapped, Mapper, mapped_column, relationship
from sqlalchemy.types import DECIMAL

from app.infra.enums import PaymentMethod
from app.models import Base, MilestonesAware
from app.models.users import User


class Check(Base, MilestonesAware):
    __tablename__ = 'checks'
    creator_id: Mapped[UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))  # indexed by default
    payment_method: Mapped[PaymentMethod] = mapped_column(nullable=False, index=True)
    paid_amount: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False, default=Decimal('0'), index=True)
    change: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False, default=Decimal('0'))
    additional_info: Mapped[str] = mapped_column(String(512), nullable=True)
    repr: Mapped[str] = mapped_column(nullable=True)

    creator: Mapped['User'] = relationship('User', back_populates='checks')
    items: Mapped[list['Item']] = relationship('Item', lazy='selectin')

    __table_args__ = (
        Index('idx_checks_creator_payment_method_date', 'creator_id', 'payment_method', 'created_at'),
        Index('idx_checks_creator_total_amount_date', 'creator_id', 'total_amount', 'created_at'),
        Index('idx_checks_creator_total_amount_date_payment_method', 'creator_id', 'total_amount', 'created_at',
              'payment_method'),
    )


class Item(Base, MilestonesAware):
    # TODO: to NORMALIZE the DB it's better to split Item table into two separates ones:
    # 1) Item with title and price fields
    # 2) CheckItem with check_id, quantity and sum fields
    __tablename__ = 'items'
    check_id: Mapped[UUID] = mapped_column(ForeignKey('checks.id', ondelete='CASCADE'))  # indexed by default
    title: Mapped[str] = mapped_column(String(512), nullable=False)  # FIXME: this should become UQ after normalization
    price: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)  # per unit or Kg
    quantity: Mapped[int] = mapped_column(nullable=False)  # units or weight (Kg)
    amount: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)  # total sum of the check item


@event.listens_for(Item, 'before_insert')
@event.listens_for(Item, 'before_update')
def on_check_item_insert_update(mapper: Mapper[Item], conn: Connection, target: Item) -> None:
    target.amount = Decimal(target.quantity * target.price).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    conn.execute(
        text("UPDATE checks SET total_amount = total_amount + :amount "
             "WHERE checks.id = :check_id"), {'amount': target.amount, 'check_id': target.check_id}
    )
    conn.execute(
        text("UPDATE checks SET change = paid_amount - total_amount "
             "WHERE checks.id = :check_id"), {'check_id': target.check_id}
    )
