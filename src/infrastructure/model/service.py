from typing import Annotated
from fastapi import Depends, HTTPException, status
from src.data import ModelRepository


class ModelService():

    def __init__(self, model_repository: Annotated[ModelRepository, Depends()]) -> None:
        self._model_repository = model_repository

    async def get_models(self, page: int, limit: int):
        return await self._model_repository.get_models(page=page, limit=limit)

    async def get_model_details(self, model_id: str):
        model_details = await self._model_repository.get_model_details(model_id=model_id)

        if model_details == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Model details could not be found!"
            )

        return model_details

    async def get_model_history(self, model_id: str):
        model_history = await self._model_repository.get_model_history(model_id=model_id)

        if model_history == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Model history could not be found!"
            )

        return model_history

    async def get_model_source(self, model_id: str, format: str = "h5"):
        model_source = await self._model_repository.get_model_source(model_id=model_id, format=format)

        if model_source == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Model source could not be found!"
            )

        return model_source

    async def get_model_input(self, model_id: str):
        model_input = await self._model_repository.get_model_input(model_id=model_id)

        if model_input == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Model input could not be found!"
            )

        return model_input
