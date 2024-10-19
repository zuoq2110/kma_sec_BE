from typing import Annotated, Optional, Any
from datetime import datetime, timezone
from bson import ObjectId
from os import sep, makedirs
from os.path import join, isfile, exists
from fastapi import Depends
from pymongo import DESCENDING
from pymongo.database import Database
from pymongo.cursor import Cursor
from src.data.local import get_database
from src.data.util import save
import os

class ModelLocalDataSource:

    def __init__(self, database: Annotated[Database, Depends(get_database)]) -> None:
        self.__collection = database["models"]

    async def insert(self, model: Optional[bytes], metadata: dict, format: str) -> ObjectId:
        document = metadata.copy()

        # Save the model's document to the database
        document["created_at"] = datetime.now(tz=timezone.utc)
        document_id = self.__collection \
            .insert_one(document=document) \
            .inserted_id

        # Save the model's file
        dir = join(".docker", "data", "files", "models", str(object=document_id))

        makedirs(name=dir, exist_ok=True)
        if model != None:
            await save(data=model, path=join(dir, f"model.{format}"))
            await save(data=bytes([]), path=join(dir, "model.tflite"))
        return document_id

    async def find_all(
        self,
        input_format: Optional[str] = None,
        state: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ) -> Cursor:
        query = {}
        fields = {"_id": 1, "version": 1, "type": 1, "input_format": 1, "state": 1, "created_at": 1}
        skip = max(0, (page - 1) * limit)

        if input_format != None:
            query['input_format'] = input_format
        if state != None:
            query['state'] = state
        return self.__collection \
            .find(query, fields) \
            .sort([('created_at', DESCENDING)]) \
            .skip(skip=skip) \
            .limit(limit=limit)

    async def find_by_id(self, model_id: str) -> Optional[Any]:
        try:
            id = ObjectId(oid=model_id)
        except:
            return None

        return self.__collection.find_one({"_id": id}, {"datasets": 0, "input": 0, "history": 0})

    async def find_datasets_by_id(self, model_id: str) -> Optional[list]:
        try:
            id = ObjectId(oid=model_id)
        except:
            return None

        document = self.__collection.find_one({"_id": id}, {"datasets": 1})

        return None if document is None else document["datasets"]

    async def find_input_by_id(self, model_id: str) -> Optional[list]:
        try:
            id = ObjectId(oid=model_id)
        except:
            return None

        document = self.__collection.find_one({"_id": id}, {"input": 1})

        return None if document is None else document["input"]

    async def find_history_by_id(self, model_id: str) -> Optional[Any]:
        try:
            id = ObjectId(oid=model_id)
        except:
            return None

        document = self.__collection.find_one({"_id": id}, {"history": 1})

        return None if document is None else document["history"]

    async def find_source_by_id(self, model_id: str, format: str) -> Optional[str]:
        try:
            id = ObjectId(oid=model_id)
            print("id",id)
        except:
            return None

        count = self.__collection.count_documents({"_id": id}, None, None, limit=1)

        if count != 1:
            return None

        # path = join(sep, "data","files", "models", model_id, f"model.{format}")
        # path = join("E:","\Code","serverkma-sec","server", ".docker", "data", "files", "models", model_id, f"model.{format}")
        path = join(".docker", "data", "files", "models", model_id,
                    f"model.{format}")

        if os.path.exists(path):
            print("File exists at path:", path)
            return path
        else:
            print("File does not exist at path:", path)

        return path if isfile(path) else None

    async def update_dataset_by_id(self, model_id: str, dataset: list) -> bool:
        try:
            id = ObjectId(oid=model_id)
        except:
            return False
        filter = {"_id": id}
        result = self.__collection.update_one(filter, { "$set": { "datasets": dataset } })

        return result.modified_count > 0

    async def update_history_by_id(self, model_id: str, history: dict) -> bool:
        try:
            id = ObjectId(oid=model_id)
        except:
            return False
        filter = {"_id": id}
        result = self.__collection.update_one(filter, { "$set": { "history": history } })

        return result.modified_count > 0

    async def update_report_by_id(self, model_id: str, report: dict) -> bool:
        try:
            id = ObjectId(oid=model_id)
        except:
            return False
        filter = {"_id": id}
        result = self.__collection.update_one(filter, { "$set": report })

        return result.modified_count > 0

    async def update_state_by_id(self, model_id: str, state: str) -> bool:
        try:
            id = ObjectId(oid=model_id)
        except:
            return False
        filter = {"_id": id}
        result = self.__collection.update_one(filter, { "$set": { "state": state } })

        return result.modified_count > 0

    async def update_source_by_id(self, model_id: str, source: bytes, format: str) -> bool:
        # Save the model's file
        # dir = join("E:","\Code","serverkma-sec","server", ".docker", "data", "files", "models", model_id, f"model.{format}")
        dir = join(".docker", "data", "files", "models", model_id, f"model.{format}")


        if not exists(path=dir):
            return False

        await save(data=source, path=join(dir, f"model.{format}"))
        return True
