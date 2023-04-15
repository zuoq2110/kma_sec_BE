from typing import Annotated
from fastapi import APIRouter, Depends, UploadFile, status
from .service import AndroidService

router = APIRouter(prefix="/android", tags=["android"])


@router.post(path="/applications", status_code=status.HTTP_201_CREATED)
async def create_application_analysis(
    file: UploadFile,
    service: Annotated[AndroidService, Depends()]
):
    analysis_id = await service.create_application_analysis(file=file)

    return {
        "message": "Create an Android application's analysis successfully.",
        "data": {
            "analysis_id": analysis_id
        }
    }


@router.get(path="/applications/{analysis_id}", status_code=status.HTTP_200_OK)
async def get_application_analysis_details(
    analysis_id: str,
    service: Annotated[AndroidService, Depends()]
):
    analysis_details = await service.get_application_analysis_details(analysis_id=analysis_id)

    return {
        "message": "Get Android application's analysis successfully.",
        "data": analysis_details
    }
