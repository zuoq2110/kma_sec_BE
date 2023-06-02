from typing import Annotated
from bson import ObjectId
from fastapi import Depends
from pymongo.database import Database
from src.data.local import get_database
from src.data.util import async_generator


class AndroidApplicationApiLocalDataSource:

    def __init__(self, database: Annotated[Database, Depends(get_database)]):
        self._collection = database["android_application_apis"]

    async def insert(self, android_application_id: ObjectId, apis: list):
        application_id = str(android_application_id)
        documents = []

        async for api in async_generator(data=apis):
            documents.append({'name': api, 'application_id': application_id})
        self._collection.insert_many(documents=documents)
