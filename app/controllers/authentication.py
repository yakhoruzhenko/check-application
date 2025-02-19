from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status

from app.infra.database import get_db
from app.models import users
from app.services import auth
from app.services.hashing import Hash

router = APIRouter(
    tags=['Authentication']
)


@router.post('/login')
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
          ) -> dict[str, str]:
    '''
    Login with the user's username (login) and password to obtain an access token
    '''
    user = db.query(users.User).filter(users.User.login == request.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'There is no user with such login: {request.username}')
    if not Hash.verify(user.password, request.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f'Invalid password for user with login: {request.username}')

    access_token = auth.create_access_token(data={'id': str(user.id)})
    return {'access_token': access_token, 'token_type': 'bearer'}
