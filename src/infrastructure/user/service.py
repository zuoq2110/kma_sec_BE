from typing import Annotated
from fastapi import Depends, UploadFile, HTTPException, status
from src.data import UserRepository
from src.domain.util import InvalidArgumentException
from src.data.local.source.user import UserCreate

class UserService:
    def __init__(self, user_respository: Annotated[UserRepository, Depends()]):
        self._user_respository = user_respository
        
    async def create_user(self, user):
        try:
            print(user)
            user = await self._user_respository.create_user(user)
            createdUser = await self._user_respository.find_user(user.inserted_id)
            return createdUser
        except InvalidArgumentException as exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(object=exception)
            )
            
   