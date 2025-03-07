from datetime import timedelta
from uuid import UUID

from fastapi import HTTPException
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette import status

from app.models import checks
from app.schemas import check


def create(db: Session, schema: check.CreateCheck) -> checks.Check:
    new_check = checks.Check(creator_id=schema.creator_id, payment_method=schema.payment.method,
                             paid_amount=schema.payment.amount, additional_info=schema.additional_info)
    db.add(new_check)
    db.flush()
    for item in schema.items:
        db.add(checks.Item(**item.model_dump(), check_id=new_check.id))
    db.commit()
    db.refresh(new_check)
    return new_check


def get_all_by_user(db: Session, creator_id: UUID, pagination_params: Params,
                    filters: check.CheckFilters) -> Page[checks.Check]:
    # Don't call 'all' method to avoid loading all query results into the memory
    stmt = select(checks.Check).filter(checks.Check.creator_id == creator_id)
    if filters.period_start:
        stmt = stmt.filter(checks.Check.created_at >= filters.period_start)
    if filters.period_end:
        # adding timdelta is needed because at the comparing time date is converted to timestamp of such format:
        # 2025-02-14 00:00:00, so when both dates are i.e. 2025-02-14, Postgres will look up for all checks
        # that were create between 2025-02-14 00:00:00 and 2025-02-14 00:00:00
        stmt = stmt.filter(checks.Check.created_at < filters.period_end + timedelta(days=1))
    if filters.total_amount_ge:
        stmt = stmt.filter(checks.Check.total_amount >= filters.total_amount_ge)
    if filters.total_amount_le:
        stmt = stmt.filter(checks.Check.total_amount <= filters.total_amount_le)
    if filters.payment_method:
        stmt = stmt.filter(checks.Check.payment_method == filters.payment_method)
    return paginate(db, stmt, params=pagination_params)  # type: ignore


def get_by_id(db: Session, id: UUID) -> checks.Check:
    # TODO: consider fetching ONLY for the creator
    selected_check = db.query(checks.Check).filter(checks.Check.id == id).first()
    if not selected_check:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Check with ID: {id} is not found')
    return selected_check


def delete(db: Session, id: UUID) -> str:  # pragma: no cover [admin]
    selected_check = db.query(checks.Check).filter(checks.Check.id == id)
    if not selected_check.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Check with ID: {id} is not found')
    selected_check.delete()
    db.commit()
    return f'Check with ID: {id} has been successfully deleted'
