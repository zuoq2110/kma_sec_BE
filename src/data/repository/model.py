from typing import Annotated, Optional
from os.path import getsize
from fastapi import Depends
from src.domain.data.model import Model, ModelDetails, ModelHistory
from src.domain.data.model.model import MODEL_TYPE_PICKLE, MODEL_SOURCE_TYPE_HDF5, MODEL_SOURCE_TYPE_PICKLE
from src.data.local import ModelLocalDataSource
from src.data.local.document import as_model, as_model_details, as_model_history


class ModelRepository:

    def __init__(self, local_data_source: Annotated[ModelLocalDataSource, Depends()]) -> None:
        self._local_data_source = local_data_source

    async def create_model(self, model: bytes, metadata: dict, format: str) -> str:
        return await self._local_data_source.insert(model=model, metadata=metadata, format=format)

    async def get_models(self, type: str = None, page: int = 1, limit: int = 20) -> list[Model]:
        cursor = await self._local_data_source.find_all(type=type, page=page, limit=limit)
        models = [as_model(document=document) for document in cursor]

        return models

    async def get_model_details(self, model_id: str) -> Optional[ModelDetails]:
        document = await self._local_data_source.find_by_id(model_id=model_id)

        if document == None:
            return None

        format = MODEL_SOURCE_TYPE_PICKLE if document['type'] == MODEL_TYPE_PICKLE else MODEL_SOURCE_TYPE_HDF5
        source = await self.get_model_source(model_id=model_id, format=format)
        size = 0 if source is None else getsize(filename=source)

        return as_model_details(document=document, source_size=size)

    async def get_model_history(self, model_id: str) -> Optional[ModelHistory]:
        document = await self._local_data_source.find_history_by_id(model_id=model_id)

        return None if document is None else as_model_history(document=document)

    async def get_model_source(self, model_id: str, format: str) -> Optional[str]:
        return await self._local_data_source.find_source_by_id(model_id=model_id, format=format)

    async def get_model_input(self, model_id: str) -> Optional[list]:
        return await self._local_data_source.find_input_by_id(model_id=model_id)
