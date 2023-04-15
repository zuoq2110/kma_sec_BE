from typing import Annotated
from datetime import datetime, timezone
from bson import ObjectId
from fastapi import Depends
from pymongo.database import Database
from src.data.local import get_database
from src.data.util import async_generator


class AndroidApplicationApiLocalDataSource:

    def __init__(self, database: Annotated[Database, Depends(get_database)]):
        self._collection = database["android_application_apis"]

    async def insert(self, android_application_id: ObjectId, apis: list):
        documents = apis.copy()
        now = datetime.now(timezone.utc)

        async for document in async_generator(data=documents):
            document["android_application_id"] = str(android_application_id)
            document["created_at"] = now
        self._collection.insert_many(documents=documents)
