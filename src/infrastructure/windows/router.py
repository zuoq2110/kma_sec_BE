from typing import Annotated
from fastapi import APIRouter, Depends, UploadFile, status
from .service import WindowsService

router = APIRouter(
    prefix="/windows",
    tags=["windows"]
)


@router.post(path="/applications", status_code=status.HTTP_201_CREATED)
async def create_application_analysis(
    file: UploadFile,
    service: Annotated[WindowsService, Depends()]
):
    analysis = await service.create_application_analysis(file=file)

    return {
        "message": "Create an Windows application's analysis successfully.",
        "data": analysis
    }


@router.get(path="/applications/{analysis_id}", status_code=status.HTTP_200_OK)
async def get_application_analysis_details(
    analysis_id: str,
    service: Annotated[WindowsService, Depends()]
):
    analysis_details = await service.get_application_analysis_details(analysis_id=analysis_id)

    return {
        "message": "Get Windows application's analysis successfully.",
        "data": analysis_details
    }
