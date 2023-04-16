from typing import Annotated, Optional, Any
from datetime import datetime, timezone
from bson import ObjectId
from os import sep
from os.path import join, isfile
from fastapi import Depends
from pymongo import DESCENDING
from pymongo.database import Database
from pymongo.cursor import Cursor
from src.data.local import get_database
from src.data.util import save


class ModelLocalDataSource:

    def __init__(self, database: Annotated[Database, Depends(get_database)]) -> None:
        self._collection = database["models"]

    async def insert(self, model: bytes, metadata: dict) -> ObjectId:
        document = metadata.copy()

        # Save the model's document to the database
        document["created_at"] = datetime.now(tz=timezone.utc)
        document_id = self._collection \
            .insert_one(document=document) \
            .inserted_id

        # Save the model's file
        dir = join(sep, "data", "files", str(object=document_id))

        save(data=model, path=join(dir, "model.h5"))

    async def find_all(self, page: int, limit: int) -> Cursor:
        skip = (page - 1) * limit

        return self._collection \
            .find({}, {"_id": 1, "version": 1, "type": 1, "created_at": 1}) \
            .sort([('date', DESCENDING)]) \
            .skip(skip=max(0, skip)) \
            .limit(limit=limit)

    async def find_by_id(self, model_id: str) -> Optional[Any]:
        id = ObjectId(oid=model_id)

        return self._collection.find_one(filter={"_id": id})

    async def find_source_by_id(self, model_id: str, format: str) -> Optional[str]:
        document = await self.find_by_id(model_id=model_id)

        if document == None:
            return None

        path = join(sep, "data", "files", model_id, f"model.{format}")

        if not isfile(path):
            return None

        return path
