from typing import Annotated,Optional
from fastapi import APIRouter, Depends, UploadFile, status
from .service import WindowsService
from ..util.jwtService import get_token

router = APIRouter(
    prefix="/windows",
    tags=["windows"]
)



@router.post(path="/applications", status_code=status.HTTP_201_CREATED)
async def create_application_analysis(
    file: UploadFile,
    service: Annotated[WindowsService, Depends()],
    token:Optional[str] = Depends(get_token),
    
):
    analysis_id = await service.create_application_analysis(file=file,token=token if token else None)
    
     # # Gửi file đến đường dẫn mới
        # async with AsyncClient() as client:
        #     response = await client.post(
        #         "http://192.168.1.103:8086/upload",
        #         files={"file": (file.filename, await file.read(), file.content_type)},
        #         data={"web_name": "KMA_SEC"}
        #     )
        #     print(response)

        # # Kiểm tra phản hồi từ server
        # response.raise_for_status()  # Raise an exception for HTTP errors

    return {
        "message": "Create an Windows application's analysis successfully.",
        "data": {"analysis_id": analysis_id}
    }


@router.get(path="/applications", status_code=status.HTTP_200_OK)
async def get_analyses(
    service: Annotated[WindowsService, Depends()],
    page: int = 1,
    limit: int = 20,
):
    analyses = await service.get_analyses(page=page, limit=limit)

    return {
        "message": "Get Windows application's analyses successfully.",
        "data": analyses
    }


@router.get(path="/applications/{analysis_id}", status_code=status.HTTP_200_OK)
async def get_analysis_details(
    analysis_id: str,
    service: Annotated[WindowsService, Depends()]
):
    analysis_details = await service.get_analysis_details(analysis_id=analysis_id)

    return {
        "message": "Get Windows application's analysis successfully.",
        "data": analysis_details
    }
