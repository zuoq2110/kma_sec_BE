import token
from typing import Annotated,Optional
from httpx import AsyncClient
from fastapi import APIRouter, Depends, UploadFile, HTTPException, status, Request
from .service import PdfService
from src.data.local.source.user import oauth2_scheme
from fastapi.responses import StreamingResponse
import httpx
from ..util.jwtService import get_token

router = APIRouter(prefix="/pdf", tags=["pdf"])

@router.post(path="/applications", status_code=status.HTTP_201_CREATED)
async def create_analysis(
    file: UploadFile,
    service: Annotated[PdfService, Depends()],
    token:Optional[str] = Depends(get_token),
):
    try:
        analysis_id = await service.create_analysis(file=file,token=token if token else None)
        print("analysis_id2:",analysis_id)
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
async def get_analysis(
    service: Annotated[PdfService, Depends()],
    page: int = 1,
    limit: int = 20,
):
    application_analysis = await service.get_analysis(page=page, limit=limit)

    return {
        "message": "Get Android application's analysis successfully.",
        "data": application_analysis
    }


@router.get(path="/applications/{analysis_id}", status_code=status.HTTP_200_OK)
async def get_analysis_details(
    analysis_id: str,
    service: Annotated[PdfService, Depends()]
):
    analysis_details = await service.get_analysis_details(analysis_id=analysis_id)

    if analysis_details == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Android application analysis details could not be found!"
        )

    return {
        "message": "Get Android application's analysis details successfully.",
        "data": analysis_details
    }

@router.get(path="/applications/{analysis_id}", status_code=status.HTTP_200_OK)
async def get_analysis_details(
    analysis_id: str,
    service: Annotated[PdfService, Depends()]
):
    analysis_details = await service.get_analysis_details(analysis_id=analysis_id)

    return {
        "message": "Get Windows application's analysis successfully.",
        "data": analysis_details
    }