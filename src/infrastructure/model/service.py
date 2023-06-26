from typing import Annotated
from fastapi import Depends
from src.data import ModelRepository


class ModelService:

    def __init__(self, model_repository: Annotated[ModelRepository, Depends()]) -> None:
        self._model_repository = model_repository

    async def get_models(self, input_format: str = None, page: int = 1, limit: int = 20):
        return await self._model_repository.get_models(input_format=input_format, page=page, limit=limit)

    async def get_model_details(self, model_id: str):
        return await self._model_repository.get_model_details(model_id=model_id)

    async def get_model_history(self, model_id: str):
        return await self._model_repository.get_model_history(model_id=model_id)

    async def get_model_source(self, model_id: str, format: str):
        return await self._model_repository.get_model_source(model_id=model_id, format=format)

    async def get_model_input(self, model_id: str):
        return await self._model_repository.get_model_input(model_id=model_id)
