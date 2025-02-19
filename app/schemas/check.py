from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, condecimal, model_validator

from app.infra.enums import PaymentMethod
from app.models.checks import Check


class Item(BaseModel):
    title: str
    price: Annotated[Decimal, condecimal(max_digits=10, decimal_places=2, gt=0)]
    quantity: int


class ItemResponse(BaseModel):
    title: str
    price: Decimal
    quantity: int
    amount: Annotated[Decimal, condecimal(max_digits=10, decimal_places=2, ge=0)]

    model_config = ConfigDict(from_attributes=True)


class Payment(BaseModel):
    method: PaymentMethod
    amount: Annotated[Decimal, condecimal(max_digits=10, decimal_places=2, gt=0)]


class CreateCheckRequest(BaseModel):
    payment: Payment = Field(..., examples=[{
        'method': PaymentMethod.CASH.value,
        'amount': '499.50'
    }])
    additional_info: str | None = Field(None, max_length=512, examples=['From loyal customer'])
    items: list[Item] = Field(..., examples=[{
        'title': 'Tomato',
        'quantity': 10,
        'price': '40.52'
    }, {
        'title': 'Potato',
        'quantity': 5,
        'price': '8.17'
    }])


class CreateCheck(CreateCheckRequest):
    creator_id: UUID


class CheckResponse(BaseModel):
    id: UUID
    items: list[ItemResponse] = Field(..., examples=[{
        'title': 'Tomato',
        'quantity': 10,
        'price': '40.52',
        'amount': '405.20'
    }, {
        'title': 'Potato',
        'quantity': 5,
        'price': '8.17',
        'amount': '40.85'
    }])
    payment: Payment = Field(..., examples=[{
        'method': PaymentMethod.CASH.value,
        'amount': '499.50'
    }])
    total_amount: Decimal = Field(..., examples=['446.05'])
    change: Decimal = Field(..., examples=['53.45'])
    # additional_info: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='before')
    @classmethod
    def map_payment_details(cls, values: Any) -> Any:
        '''
        Map plain payment_method and paid_amount to nested Payment object
        '''
        if not isinstance(values, Check):
            return values  # pragma: no cover

        check_values = {k: getattr(values, k) for k in values.__table__.columns.keys()}

        if 'payment' not in check_values:  # pragma: no branch
            check_values['payment'] = Payment(
                method=check_values.get('payment_method'),  # type: ignore
                amount=check_values.get('paid_amount'),  # type: ignore
            )
        if 'items' not in check_values:  # pragma: no branch
            check_values['items'] = values.items
        return check_values


class CheckFilters(BaseModel):
    period_start: date | None = None
    period_end: date | None = None
    total_amount_ge: Decimal | None = None
    total_amount_le: Decimal | None = None
    payment_method: PaymentMethod | None = None
