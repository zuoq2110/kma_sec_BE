from typing import Annotated
from bson import ObjectId
from fastapi import Depends, HTTPException, status
from pymongo.database import Database
from src.data.local import get_database
from src.data.util import async_generator
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from pydantic import BaseModel, Field


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = "duongdeptrai"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
class UserCreate(BaseModel):
    username: str
    password: str
    isAdmin: bool = Field(default=False)

class UserLocalDataSource:

    def __init__(self, database: Annotated[Database, Depends(get_database)]):
        self._collection = database["user"]

    async def insert(self, user):
        print("model metadata",user)
        db_user = self.get_user_by_username(user.username)
        if db_user:
            raise HTTPException(status_code=400, detail="Username already registered!")
        password = pwd_context.hash(user.password)
        document = {
            "username": user.username,
            "password": password,
            "isAdmin": user.isAdmin
        }
        print("self._collection:",self._collection)
        
        return self._collection \
            .insert_one(document=document)
            
    async def find_one(self, id):
        try:
            print("id", id)
            print("self._collection:", self._collection)
            
            # Chuyển đổi id thành ObjectId
            result =  self._collection.find_one({"_id": ObjectId(id)})
            print("result:", result)
            
            if result is None:
                return None  # Hoặc raise HTTPException nếu cần
            
            # Chuyển đổi ObjectId thành string nếu cần
            result["_id"] = str(result["_id"])
            return result  # Trả về dict
        except Exception as e:
            print("Error:", e)
            return None  # Hoặc raise lỗi khác nếu cần
        
    def get_user_by_username(self, username: str):
        return self._collection.find_one({"username": username})
    

    def authenticate_user(self,username: str, password: str):
        user = self._collection.find_one({"username": username})
        if not user:
            return False
        if not pwd_context.verify(password, user['password']):
            return False
        return user
    
    def create_access_token(self,data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
        
    def login_for_access_token(self,form_data):
        user = self.authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        access_token = self.create_access_token(
            data ={"sub": user["username"]}, expires_delta=access_token_expires
        )
        return {"id": str(user["_id"]),"sub": user["username"],"access_token": access_token,"isAdmin": user["isAdmin"], "token_type": "bearer"}
    
    def verify_token(self,token: str = Depends(oauth2_scheme)):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(status_code=403, detail="Token is invalid or expired")
            return payload
        except JWTError:
            raise HTTPException(status_code=403, detail="Token is invalid or expired")
        
    async def check_username(self, username: str) -> bool:
        user = self._collection.find_one({"username": username})
        return user is not None
    
    
