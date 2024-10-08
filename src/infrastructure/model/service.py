from typing import Annotated, Optional
from re import search
from fastapi import Depends, UploadFile
from src.domain.data.model import ModelInputFormat, ModelState, ModelSourceFormat
from src.domain.util import InvalidArgumentException
from src.data import ModelRepository
from src.data.util import async_generator


class ModelService:

    def __init__(self, model_repository: Annotated[ModelRepository, Depends()]) -> None:
        self.__model_repository = model_repository

    async def create_model(self, version: str, model_id: str, dataset: list[UploadFile], epoch: int):
        files = []

        async for file in async_generator(data=dataset):
            content = file.read()
            label = search(r"_(.*?)[.]", file.filename).group(1)

            files.append({"label": label, "content": await content})
        await self.__model_repository.create_model(version, model_id, files, epoch)

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
        try:
            format = ModelSourceFormat(value=format)
        except ValueError:
            raise InvalidArgumentException("Model source format is invalid!")
        return await self.__model_repository.get_model_source(model_id=model_id, format=format)

    async def update_model_state(self, model_id: str, state: str):
        try:
            state = None if state is None else ModelState(value=state)
        except ValueError:
            raise InvalidArgumentException("Model state is invalid!")

        if state == ModelState.TRAINING:
            raise InvalidArgumentException("Model state is invalid!")

        await self.__model_repository.update_model_state(model_id=model_id, state=state)
