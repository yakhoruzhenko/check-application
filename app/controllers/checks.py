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
    Create a new check
    '''
    schema = check.CreateCheck(**request.model_dump(), creator_id=current_user.id)
    # TODO: consider validation for cases when change is less than zero
    new_check = check_repo.create(db, schema)
    response.headers['X-Check-Text-Link'] = jsonable_encoder(get_response_url(fastapi_request, new_check.id))
    return check.CheckResponse.model_validate(new_check)


@router.get('/own', status_code=status.HTTP_200_OK)
def get_own_checks(db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user),
                   pagination_params: Params = Depends(),
                   period_start: date = Query(None, description='Filter by check creation date start (included)',
                                              example='2025-02-14'),
                   period_end: date = Query(None, description='Filter by check creation date end (included)',
                                            example='2025-04-15'),
                   total_amount_ge: Decimal = Query(None, description='Filter by total amount (greater or equal)',
                                                    example='149.99'),
                   total_amount_le: Decimal = Query(None, description='Filter by total amount (less or equal)',
                                                    example='500.00'),

                   payment_method: PaymentMethod = Query(None, description='Filter by payment method')
                   ) -> Page[check.CheckResponse]:
    '''
    Retrieve all checks for the current user
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
    Retrieve a specific check by its ID
    '''
    response.headers['X-Check-Text-Link'] = jsonable_encoder(get_response_url(request, id))
    return check.CheckResponse.model_validate(check_repo.get_by_id(db, id))


@router.get('/{id}/text', responses={
    status.HTTP_200_OK: {
        "description": "Successful check text representation",
        "content": {
            "text/html": {
                "example":
                '<pre>Temperature-resistant Weather-resistant '
                '\n           Products 1562 LLC            '
                '\n========================================'
                '\n10.00 x 40.52'
                '\nTomato                            405.20'
                '\n----------------------------------------'
                '\n5.00 x 8.17'
                '\nPotato                             40.85'
                '\n========================================'
                '\nTOTAL                             446.05'
                '\nCash                              499.50'
                '\nChange                             53.45'
                '\n========================================'
                '\n'
                '            19.02.2025 16:09            \n'
                '      Thank you for your purchase!      </pre>'
            }
        }
    }
})
def get_check_text_repr_by_id(id: UUID, db: Session = Depends(get_db)) -> Response:
    '''
    Retrieve the textual representation of a specific check by its ID
    '''
    existing_check = check_repo.get_by_id(db, id)
    text = existing_check.repr
    if not text:
        text = built_text_representation(existing_check)
        existing_check.repr = text
        db.add(existing_check)
        db.commit()
    return Response(content=f'<pre>{text}</pre>', media_type='text/html; charset=utf-8')
