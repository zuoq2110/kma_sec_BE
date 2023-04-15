from typing import Annotated, Optional, Any
from datetime import datetime, timezone
from bson import ObjectId
from fastapi import Depends
from pymongo.database import Database
from src.data.local import get_database


class AndroidApplicationLocalDataSource:

    def __init__(self, database: Annotated[Database, Depends(get_database)]) -> None:
        self._collection = database["android_applications"]

    async def insert(self, metadata: dict, malware_type: str) -> ObjectId:
        document = metadata.copy()

        document["malware_type"] = malware_type
        document["created_at"] = datetime.now(timezone.utc)
        return self._collection \
            .insert_one(document=document) \
            .inserted_id

    async def find_by_id(self, document_id: ObjectId) -> Optional[Any]:
        filter = {"_id": document_id}

        return self._collection.find_one(filter, {"created_at": 0})

    async def find_by_package(self, package: str) -> Optional[Any]:
        filter = {"package": package}

        return self._collection.find_one(filter, {"created_at": 0})
