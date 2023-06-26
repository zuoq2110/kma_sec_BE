from typing import Annotated
from fastapi import APIRouter, Depends, UploadFile, HTTPException, status
from .service import AndroidService

router = APIRouter(prefix="/android", tags=["android"])


@router.post(path="/applications", status_code=status.HTTP_201_CREATED)
async def create_application_analysis(
    file: UploadFile,
    service: Annotated[AndroidService, Depends()]
):
    try:
        analysis_id = await service.create_application_analysis(file=file)
    except Exception as exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(object=exception)
        )

    return {
        "message": "Create an Android application's analysis successfully.",
        "data": {"analysis_id": analysis_id}
    }


@router.get(path="/applications", status_code=status.HTTP_200_OK)
async def get_application_analysis(
    service: Annotated[AndroidService, Depends()],
    page: int = 1,
    limit: int = 20,
):
    application_analysis = await service.get_application_analysis(page=page, limit=limit)

    return {
        "message": "Get Android application's analysis successfully.",
        "data": application_analysis
    }


@router.get(path="/applications/{analysis_id}", status_code=status.HTTP_200_OK)
async def get_application_analysis_details(
    analysis_id: str,
    service: Annotated[AndroidService, Depends()]
):
    analysis_details = await service.get_application_analysis_details(analysis_id=analysis_id)

    if analysis_details == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Android application analysis details could not be found!"
        )

    return {
        "message": "Get Android application's analysis details successfully.",
        "data": analysis_details
    }
