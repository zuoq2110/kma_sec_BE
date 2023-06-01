from typing import Annotated
from fastapi import APIRouter, Depends, status
from fastapi.responses import FileResponse
from .service import ModelService


router = APIRouter(prefix="/models", tags=["models"])


@router.get(path="", status_code=status.HTTP_200_OK)
async def get_models(
    service: Annotated[ModelService, Depends()],
    limit: int = 20,
    page: int = 0
):
    models = await service.get_models(limit=limit, page=page)

    return {
        "message": "Get models successfully.",
        "data": models
    }


@router.get(path="/{model_id}", status_code=status.HTTP_200_OK)
async def get_model_details(
    model_id: str,
    service: Annotated[ModelService, Depends()]
):
    model_details = await service.get_model_details(model_id=model_id)

    return {
        "message": "Get model details successfully.",
        "data": model_details
    }


@router.get(path="/{model_id}/history", status_code=status.HTTP_200_OK)
async def get_model_history(
    model_id: str,
    service: Annotated[ModelService, Depends()]
):
    model_history = await service.get_model_history(model_id=model_id)

    return {
        "message": "Get model history successfully.",
        "data": model_history
    }


@router.get(path="/{model_id}/source", status_code=200)
async def get_model_source(
    model_id: str,
    format: str,
    service: Annotated[ModelService, Depends()],
) -> FileResponse:
    model_source = await service.get_model_source(model_id=model_id, format=format)

    return FileResponse(
        path=model_source,
        media_type='application/octet-stream',
        filename=f"model.{format}"
    )


@router.get(path="/{model_id}/input", status_code=status.HTTP_200_OK)
async def get_model_input(
    model_id: str,
    service: Annotated[ModelService, Depends()]
):
    model_input = await service.get_model_input(model_id=model_id)

    return {
        "message": "Get model input successfully.",
        "data": model_input
    }
