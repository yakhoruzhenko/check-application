from typing import cast
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi_pagination import Page, Params
from sqlalchemy.orm import Session
from starlette import status

from app.infra.database import get_db
from app.repositories import check
from app.repositories import user as user_repo
from app.schemas import user
from app.services.auth import admin_token

router = APIRouter(
    prefix='/admin',
    tags=['Fake Admin Panel']
)


@router.get('/users/{id}', status_code=status.HTTP_200_OK)
def get_user_by_id(id: UUID, db: Session = Depends(get_db),
                   fake_valitaton: None = Depends(admin_token)) -> user.UserResponse:
    return user.UserResponse.model_validate(user_repo.get_by_id(id, db))


@router.get('/users', status_code=status.HTTP_200_OK)
def get_all_users(db: Session = Depends(get_db),
                  fake_valitaton: None = Depends(admin_token),
                  pagination_params: Params = Depends()) -> Page[user.UserResponse]:
    return cast(Page[user.UserResponse], user_repo.get_all(db, pagination_params))


@router.delete('/users/{id}', status_code=status.HTTP_200_OK)
def delete_by_user_id(id: UUID, db: Session = Depends(get_db), fake_valitaton: None = Depends(admin_token)) -> str:
    return user_repo.delete(id, db)


@router.put('/users/{id}/password', status_code=status.HTTP_204_NO_CONTENT)
def reset_user_password(id: UUID, request: user.ResetUserPasswordRequest, db: Session = Depends(get_db),
                        fake_valitaton: None = Depends(admin_token)) -> None:
    user_repo.reset_password(user.ResetUserPassword(**request.model_dump(), user_id=id), db)


@router.delete('/checks/{id}', status_code=status.HTTP_200_OK)
def delete(id: UUID, db: Session = Depends(get_db), fake_valitaton: None = Depends(admin_token)) -> str:
    return check.delete(db, id)
