from typing import Annotated
from bson import ObjectId
from fastapi import Depends
from src.data.local import AndroidApplicationApiLocalDataSource


class AndroidApplicationApiRepository:

    def __init__(self, local_data_source: Annotated[AndroidApplicationApiLocalDataSource, Depends()]):
        self._local_data_source = local_data_source

    async def create_application_apis(self, application_id: ObjectId, apis: list):
        return await self._local_data_source.insert(android_application_id=application_id, apis=apis)
