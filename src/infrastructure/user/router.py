from typing import Annotated
from fastapi import APIRouter, Depends, UploadFile, status
from .service import UserService
from src.data.local.source.user import UserLocalDataSource 
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from src.data.local.source.user import UserCreate

router = APIRouter(prefix="/user", tags=["user"])



@router.post(path="/register", status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    service: Annotated[UserService, Depends()]
):
    print(user)
    user = await service.create_user(user)
    return {
        "message": "Request to create model has been accepted.",
        "data": user
    }
    
@router.post(path="/token",status_code=status.HTTP_201_CREATED)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: UserLocalDataSource = Depends()):
    result =service.login_for_access_token(form_data)
    return result

@router.get(path="/verify-token/{token}")
async def verify_user_token(token: str, user: Annotated[UserLocalDataSource, Depends()]):
    user.verify_token(token=token)
    return {
        "message": "Successfully!",
    }
    
@router.get("/existsByUsername")
async def check_username(username: str, user: Annotated[UserLocalDataSource, Depends()]) -> bool:
    exists = await user.check_username(username=username)
    return exists