import os
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from fastapi import Depends, Header, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm.session import Session
from starlette import status

from app.infra.database import get_db
from app.models.users import User
from app.repositories.user import get_by_id

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')


SECRET_KEY = os.getenv('SECRET_KEY',
                       'fcb83a311c0ab22310e16417b84de96d496c5f80906b4e14c00b15de44f56a8c')
ADMIN_TOKEN = os.getenv('ADMIN_TOKEN', 'fake_token')
ALGORITHM = os.getenv('HASHING_ALGOTRITHM', 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE', 30))


def create_access_token(data: dict[str, Any]) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=float(ACCESS_TOKEN_EXPIRE_MINUTES))
    data.update({'exp': expire})
    encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme),
                     db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: UUID = payload.get('id')  # type: ignore[assignment]
        if user_id is None:  # pragma: no cover
            raise credentials_exception
    except JWTError:  # pragma: no cover
        raise credentials_exception
    return get_by_id(id=user_id, db=db)


def admin_token(x_admin_token: str = Header()) -> None:  # pragma: no cover
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid admin token',
        )
