from typing import Annotated
from datetime import datetime, timezone
from bson import ObjectId
from fastapi import Depends
from pymongo.database import Database
from src.data.local import get_database


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
