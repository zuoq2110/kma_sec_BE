from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from src.domain.util import InvalidArgumentException
from .service import ModelService


router = APIRouter(prefix="/models", tags=["models"])


@router.get(path="", status_code=status.HTTP_200_OK)
async def get_models(
    service: Annotated[ModelService, Depends()],
    input_format: Optional[str] = None,
    state: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
):
    try:
        models = await service.get_models(input_format=input_format, state=state, page=page, limit=limit)
    except InvalidArgumentException as exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exception)
        )

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

    if model_details == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model details could not be found!"
        )

    return {
        "message": "Get model details successfully.",
        "data": model_details
    }


@router.get(path="/{model_id}/datasets", status_code=status.HTTP_200_OK)
async def get_model_datasets(
    model_id: str,
    service: Annotated[ModelService, Depends()]
):
    model_datasets = await service.get_model_datasets(model_id=model_id)

    if model_datasets == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model datasets could not be found!"
        )

    return {
        "message": "Get model datasets successfully.",
        "data": model_datasets
    }


@router.get(path="/{model_id}/input", status_code=status.HTTP_200_OK)
async def get_model_input(
    model_id: str,
    service: Annotated[ModelService, Depends()]
):
    model_input = await service.get_model_input(model_id=model_id)

    if model_input == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model input could not be found!"
        )

    return {
        "message": "Get model input successfully.",
        "data": model_input
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


@router.get(path="/{model_id}/source", status_code=status.HTTP_200_OK)
async def get_model_source(
    model_id: str,
    format: str,
    service: Annotated[ModelService, Depends()],
) -> FileResponse:
    model_source = await service.get_model_source(model_id=model_id, format=format)

    if model_source == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model source could not be found!"
        )

    return FileResponse(
        path=model_source,
        media_type='application/octet-stream',
        filename=f"model.{format}"
    )
