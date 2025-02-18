from datetime import date
from decimal import Decimal
from typing import cast
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi_pagination import Page, Params
from sqlalchemy.orm import Session
from starlette import status

from app.controllers import get_response_url
from app.infra.database import get_db
from app.infra.enums import PaymentMethod
from app.models.users import User
from app.repositories import check as check_repo
from app.schemas import check
from app.services.auth import get_current_user
from app.services.check_builder import built_text_representation

router = APIRouter(
    prefix='/checks',
    tags=['Checks']
)


@router.post('', status_code=status.HTTP_201_CREATED)
def create_check(request: check.CreateCheckRequest, fastapi_request: Request,
                 response: Response, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)) -> check.CheckResponse:
    '''
    Create a new Check
    '''
    schema = check.CreateCheck(**request.model_dump(), creator_id=current_user.id)
    # TODO: consider validation for cases when change is less than zero
    new_check = check_repo.create(db, schema)
    response.headers['X-Check-Text-Link'] = jsonable_encoder(get_response_url(fastapi_request, new_check.id))
    return check.CheckResponse.model_validate(new_check)


@router.get('', status_code=status.HTTP_200_OK)
def get_own_checks(db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user),
                   pagination_params: Params = Depends(),
                   period_start: date = Query(None, description='Filter by check creation date start (included)',
                                              example='2025-02-14'),
                   period_end: date = Query(None, description='Filter by check creation date end (included)',
                                            example='2025-02-15'),
                   total_amount_ge: Decimal = Query(None, description='Filter by total amount (greater or equal)',
                                                    example='149.99'),
                   total_amount_le: Decimal = Query(None, description='Filter by total amount (less or equal)',
                                                    example='500.00'),

                   payment_method: PaymentMethod = Query(None, description='Filter by payment method')
                   ) -> Page[check.CheckResponse]:
    '''
    Get all existing Checks of the current User
    '''
    filters = check.CheckFilters(
        period_start=period_start,
        period_end=period_end,
        total_amount_ge=total_amount_ge,
        total_amount_le=total_amount_le,
        payment_method=payment_method,
    )
    return cast(Page[check.CheckResponse], check_repo.get_all_by_user(db, current_user.id, pagination_params, filters))


@router.get('/{id}', status_code=status.HTTP_200_OK)
def get_check_by_id(id: UUID, request: Request, response: Response, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)) -> check.CheckResponse:
    '''
    Get specific existing Check by its ID
    '''
    response.headers['X-Check-Text-Link'] = jsonable_encoder(get_response_url(request, id))
    return check.CheckResponse.model_validate(check_repo.get_by_id(db, id))


@router.get('/{id}/text', responses={
    status.HTTP_200_OK: {
        "description": "Successful check text representation",
        "content": {
            "text/html": {
                "example":
                '''
                <pre>    Weather-resistant Handmade Smart
                            Products 511 Co.
                    ========================================
                    3.00 x 75.36
                    Compact Top-tier
                    Professional Hygienic Modern
                    Advanced Vintage Item             226.08
                    ----------------------------------------
                    3.00 x 10.92
                    All-season Handmade
                    Sustainable Anti-slip
                    Affordable Item                    32.76
                    ----------------------------------------
                    1.00 x 51.72
                    Classic High-quality
                    Customizable Professional
                    Exclusive Sustainable Vegan
                    Item                               51.72
                    ----------------------------------------
                    1.00 x 24.93
                    Stackable Colorful Classic
                    Recyclable Eco-friendly
                    Fast-charging Heavy-duty
                    Compact Custom Item                24.93
                    ----------------------------------------
                    4.00 x 11.77
                    Heavy-duty Trendy High-
                    performance Item                   47.08
                    ========================================
                    TOTAL                             382.57
                    Cash                              446.49
                    Change                             63.92
                    ========================================
                                05.03.2025 06:30
                        Thank you for your purchase!      </pre>
                '''
            }
        }
    }
})
def get_check_text_repr_by_id(id: UUID, db: Session = Depends(get_db)) -> Response:
    '''
    Get specific existing Check textual representation by its ID
    '''
    existing_check = check_repo.get_by_id(db, id)
    text = existing_check.repr
    if not text:
        text = built_text_representation(existing_check)
        existing_check.repr = text
        db.add(existing_check)
        db.commit()
    return Response(content=f'<pre>{text}</pre>', media_type='text/html; charset=utf-8')
