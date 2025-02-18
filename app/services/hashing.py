from typing import Any

from fastapi import HTTPException
from passlib.context import CryptContext
from passlib.exc import UnknownHashError
from starlette import status

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Hash:
    @staticmethod
    def bcrypt(password: str) -> Any:
        return pwd_ctx.hash(password)

    @staticmethod
    def verify(hashed_password: str, plain_password: str) -> Any:
        try:
            return pwd_ctx.verify(plain_password, hashed_password)
        except UnknownHashError as exc:  # pragma: no cover
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail=f'{exc}')
