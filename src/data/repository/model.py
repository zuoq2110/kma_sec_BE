from typing import Annotated, Optional
from os.path import getsize
from fastapi import Depends
from src.domain.data.model.model import *
from src.data.local import ModelLocalDataSource
from src.data.local.document import as_model, as_model_details, as_model_dataset, as_model_history


class ModelRepository:

    def __init__(self, local_data_source: Annotated[ModelLocalDataSource, Depends()]) -> None:
        self._local_data_source = local_data_source

    async def create_model(self, model: bytes, metadata: dict, format: str) -> str:
        return await self._local_data_source.insert(model=model, metadata=metadata, format=format)

    async def get_models(
        self,
        input_format: Optional[ModelInputFormat] = None,
        state: Optional[ModelState] = None,
        page: int = 1,
        limit: int = 20
    ) -> list[Model]:
        cursor = await self._local_data_source.find_all(
            input_format=None if input_format is None else input_format.value,
            state=None if state is None else state.value,
            page=page,
            limit=limit
        )
        models = [as_model(document=document) for document in cursor]

        return models

    async def get_model_details(self, model_id: str) -> Optional[ModelDetails]:
        document = await self._local_data_source.find_by_id(model_id=model_id)

        if document == None:
            return None

        format = ModelSourceFormat.PICKLE if document['type'] == ModelType.PICKLE.value else ModelSourceFormat.HDF5
        source = await self.get_model_source(model_id=model_id, format=format)
        size = 0 if source is None else getsize(filename=source)

        return as_model_details(document=document, source_size=size)

    async def get_model_datasets(self, model_id: str) -> Optional[list]:
        documents = await self._local_data_source.find_datasets_by_id(model_id=model_id)

        return None if documents is None else [as_model_dataset(document=document) for document in documents]

    async def get_model_history(self, model_id: str) -> Optional[ModelHistory]:
        document = await self._local_data_source.find_history_by_id(model_id=model_id)

        return None if document is None else as_model_history(document=document)

    async def get_model_source(self, model_id: str, format: ModelSourceFormat) -> Optional[str]:
        return await self._local_data_source.find_source_by_id(model_id=model_id, format=format.value)

    async def get_model_input(self, model_id: str) -> Optional[list]:
        return await self._local_data_source.find_input_by_id(model_id=model_id)
