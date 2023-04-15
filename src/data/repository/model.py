from typing import Annotated, Optional
from os.path import getsize
from datetime import timezone
from fastapi import Depends
from src.data.local import ModelLocalDataSource
from src.domain.data.model import Model, ModelDetails


class ModelRepository:

    def __init__(self, local_data_source: Annotated[ModelLocalDataSource, Depends()]) -> None:
        self._local_data_source = local_data_source

    async def get_models(self, page: int, limit: int) -> list[Model]:
        cursor = await self._local_data_source.get_models(page=page, limit=limit)
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
            created_at=document['created_at']
                .replace(tzinfo=timezone.utc)
                .isoformat()
        )

    async def get_model_details(self, model_id: str) -> Optional[ModelDetails]:
        document = await self._local_data_source.get_model_details(model_id=model_id)

        if document == None:
            return None

        source = await self.get_model_source(model_id=model_id)
        size = 0 if source is None else getsize(filename=source)

        return self._as_model_details(document=document, source_size=size)

    def _as_model_details(self, document, source_size: int) -> ModelDetails:
        return ModelDetails(
            id=str(object=document['_id']),
            version=document['version'],
            type=document['type'],
            size=source_size,
            input=document['input'],
            output=document['output'],
            accuracy=document['accuracy'],
            loss=document['loss'],
            precision=document['precision'],
            recall=document['recall'],
            f1=document['f-1'],
            history=document['history'],
            created_at=document['created_at']
                .replace(tzinfo=timezone.utc)
                .isoformat()
        )

    async def get_model_source(self, model_id: str, format: str = "h5") -> Optional[str]:
        return await self._local_data_source.get_model_source(model_id=model_id, format=format)
