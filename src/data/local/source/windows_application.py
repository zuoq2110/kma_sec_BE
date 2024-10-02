from typing import Annotated, Optional, Any
from datetime import datetime, timezone
from bson import ObjectId
from fastapi import Depends
from pymongo import DESCENDING
from pymongo.database import Database
from pymongo.cursor import Cursor
from src.data.local import get_database
import jwt


class WindowsApplicationLocalDataSource:

    def __init__(self, database: Annotated[Database, Depends(get_database)]) -> None:
        self._collection = database["windows_applications"]

    async def insert(self, metadata: dict, malware_type: str) -> ObjectId:
        document = metadata.copy()

        document["malware_type"] = malware_type
        document["created_at"] = datetime.now(timezone.utc)
        return self._collection \
            .insert_one(document=document) \
            .inserted_id

    async def find_all(self, page: int = 1, limit: int = 20) -> Cursor:
        skip = max(0, (page - 1) * limit)

        return self._collection \
            .find({}, {"_id": 1, "md5": 1, "malware_type": 1, "created_at": 1}) \
            .sort([('created_at', DESCENDING)]) \
            .skip(skip=skip) \
            .limit(limit=limit)

    async def find_by_id(self, document_id: ObjectId) -> Optional[Any]:
        return self._collection.find_one({"_id": document_id})
