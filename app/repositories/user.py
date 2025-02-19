from uuid import UUID

from fastapi import HTTPException
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette import status

from app.models import users
from app.schemas import user
from app.services.hashing import Hash


def create(request: user.CreateUserRequest, db: Session) -> users.User:
    new_user = users.User(name=request.name, email=request.email, login=request.login,
                          password=Hash.bcrypt(request.password))
    db.add(new_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=f'User with login: {request.login} already exists')
    return new_user


def reset_password(request: user.ResetUserPassword, db: Session) -> None:  # pragma: no cover [admin]
    user = db.query(users.User).filter(users.User.id == request.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'There is no user with ID: {request.user_id}'
        )
    user.password = Hash.bcrypt(request.new_password)
    db.add(user)
    db.commit()


def get_all(db: Session, pagination_params: Params) -> Page[users.User]:  # pragma: no cover [admin]
    return paginate(db.query(users.User), params=pagination_params)  # type: ignore


def get_by_id(id: UUID, db: Session) -> users.User:
    user = db.query(users.User).filter(users.User.id == id).first()
    if not user:  # pragma: no cover [admin]
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'User with ID: {id} is not found')
    return user


def delete(id: UUID, db: Session) -> str:  # pragma: no cover [admin]
    user = db.query(users.User).filter(users.User.id == id)
    if not user.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'User with ID: {id} is not found')
    user.delete()
    db.commit()
    return f'User with ID: {id} has been successfully deleted'
