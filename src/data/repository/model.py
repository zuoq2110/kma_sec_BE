from typing import Annotated, Optional
from os.path import getsize
from fastapi import Depends
from src.data.local import ModelLocalDataSource
from src.domain.data.model import Model, ModelDetails, ModelHistory


class ModelRepository:

    def __init__(self, local_data_source: Annotated[ModelLocalDataSource, Depends()]) -> None:
        self._local_data_source = local_data_source

    async def create_model(self, model: bytes, metadata: dict, format: str) -> str:
        return await self._local_data_source.insert(model=model, metadata=metadata, format=format)

    async def get_models(self, type: str = None, page: int = 1, limit: int = 20) -> list[Model]:
        cursor = await self._local_data_source.find_all(type=type, page=page, limit=limit)
        models = []

        for document in cursor:
            model = self._as_model(document=document)

            models.append(model)
        return models

    def _as_model(self, document) -> Model:
        return Model(
            id=str(object=document['_id']),
            version=document['version'],
            type=document['type'],
            created_at=document['created_at'].isoformat()
        )

    async def get_model_details(self, model_id: str) -> Optional[ModelDetails]:
        document = await self._local_data_source.find_by_id(model_id=model_id)

        if document == None:
            return None

        format = 'pickle' if document['type'] == 'PICKLE' else 'h5'
        source = await self.get_model_source(model_id=model_id, format=format)
        size = 0 if source is None else getsize(filename=source)

        return self._as_model_details(document=document, source_size=size)

    def _as_model_details(self, document, source_size: int) -> ModelDetails:
        return ModelDetails(
            id=str(object=document['_id']),
            version=document['version'],
            type=document['type'],
            size=source_size,
            datasets=document['datasets'],
            output=document['output'],
            accuracy=document['accuracy'],
            loss=document['loss'],
            precision=document['precision'],
            recall=document['recall'],
            f1=document['f1'],
            created_at=document['created_at'].isoformat()
        )

    async def get_model_history(self, model_id: str) -> Optional[ModelHistory]:
        document = await self._local_data_source.find_history_by_id(model_id=model_id)

        return None if document is None else self._as_model_history(document=document)

    def _as_model_history(self, document) -> ModelHistory:
        return ModelHistory(
            accuracy=document['accuracy'],
            val_accuracy=document['val_accuracy'],
            loss=document['loss'],
            val_loss=document['val_loss'],
        )

    async def get_model_source(self, model_id: str, format: str) -> Optional[str]:
        return await self._local_data_source.find_source_by_id(model_id=model_id, format=format)

    async def get_model_input(self, model_id: str) -> Optional[list]:
        return await self._local_data_source.find_input_by_id(model_id=model_id)
