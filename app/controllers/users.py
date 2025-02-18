from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from app.infra.database import get_db
from app.models.users import User
from app.repositories import user as user_repo
from app.schemas import user
from app.services.auth import get_current_user

router = APIRouter(
    prefix='/users',
    tags=['Users']
)


@router.post('', status_code=status.HTTP_201_CREATED)
def create_user(request: user.CreateUserRequest, db: Session = Depends(get_db)) -> user.UserResponse:
    '''
    Register a new user
    '''
    return user.UserResponse.model_validate(user_repo.create(request, db))


@router.get('/profile', status_code=status.HTTP_200_OK)
def get_current_user_profile(db: Session = Depends(get_db),
                             current_user: User = Depends(get_current_user)) -> user.UserResponseWithChecks:
    '''
    Retrieve the current user's registration data and checks
    '''
    return user.UserResponseWithChecks.model_validate(user_repo.get_by_id(current_user.id, db))
