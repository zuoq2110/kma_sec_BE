from typing import Annotated, Optional
from fastapi import Depends
from src.domain.data.model import ModelInputFormat, ModelState
from src.domain.util import InvalidArgumentException
from src.data import ModelRepository


class ModelService:

    def __init__(self, model_repository: Annotated[ModelRepository, Depends()]) -> None:
        self.__model_repository = model_repository

    async def get_models(
        self,
        input_format: Optional[str] = None,
        state: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ):
        try:
            state = None if state is None else ModelState(value=state)
        except ValueError:
            raise InvalidArgumentException("Model state is invalid!")
        try:
            input_format = None if input_format is None else ModelInputFormat(value=input_format)
        except ValueError:
            raise InvalidArgumentException("Model input format is invalid!")

        return await self.__model_repository.get_models(
            input_format=input_format,
            state=state,
            page=page,
            limit=limit
        )

    async def get_model_details(self, model_id: str):
        return await self.__model_repository.get_model_details(model_id=model_id)

    async def get_model_datasets(self, model_id: str):
        return await self.__model_repository.get_model_datasets(model_id=model_id)

    async def get_model_input(self, model_id: str):
        return await self.__model_repository.get_model_input(model_id=model_id)

    async def get_model_history(self, model_id: str):
        return await self.__model_repository.get_model_history(model_id=model_id)

    async def get_model_source(self, model_id: str, format: str):
        return await self.__model_repository.get_model_source(model_id=model_id, format=format)
