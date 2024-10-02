from typing import Annotated, Optional, Any
from datetime import datetime, timezone
from bson import ObjectId
from fastapi import Depends,HTTPException
from pymongo import DESCENDING
from pymongo.database import Database
from pymongo.cursor import Cursor
from src.data.local import get_database
import jwt
from .user import SECRET_KEY,ALGORITHM,oauth2_scheme

class AndroidApplicationLocalDataSource:

    def __init__(self, database: Annotated[Database, Depends(get_database)]) -> None:
        self._collection = database["android_applications"]
        self._user_collection = database['user']
        
    async def get_object_id_by_sub(self, sub: str) -> ObjectId:
        user_document = self._user_collection.find_one({"username": sub})  # Tìm kiếm theo sub
        if user_document:
            return user_document["_id"]  # Lấy ObjectId từ tài liệu
        else:
            raise Exception("User not found")
        
    def decode_token(self, token: str):
        try:
            # Giải mã token
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.PyJWTError:
            raise HTTPException(status_code=403, detail="Invalid token")

    async def insert(self, metadata: dict, malware_type: str, token: Optional[str]) -> ObjectId:
        try:
            if token:  # Kiểm tra xem token có tồn tại không
                payload = self.decode_token(token)
            
                sub = payload.get("sub")  # Lấy sub từ token

            # Lấy ObjectId từ sub
                created_by = await self.get_object_id_by_sub(sub)
                metadata["created_by"] = created_by  # Thêm created_by vào tài liệu
            else:
                print("No token provided. Skipping created_by.")

        except jwt.ExpiredSignatureError:
            raise Exception("Token has expired")
        except jwt.InvalidTokenError:
            raise Exception("Invalid token")
        
        document = metadata.copy()

        document["malware_type"] = malware_type
        document["created_at"] = datetime.now(timezone.utc)
        
        return self._collection \
            .insert_one(document=document) \
            .inserted_id

    async def find_all(self, page: int = 1, limit: int = 20) -> Cursor:
        skip = max(0, (page - 1) * limit)

        return self._collection \
            .find({}, {"user_features": 0, "permissions": 0, "activities": 0, "services": 0, "receivers": 0}) \
            .sort([('created_at', DESCENDING)]) \
            .skip(skip=skip) \
            .limit(limit=limit)

    async def find_by_id(self, document_id: ObjectId) -> Optional[Any]:
        filter = {"_id": document_id}

        return self._collection.find_one(filter)

    async def find_by_certificate(self, package: str, certificate: dict) -> Optional[Any]:
        certificates = {"$elemMatch": certificate}
        filter = {
            "package": package,
            "certificates": certificates
        }

        return self._collection.find_one(filter)
