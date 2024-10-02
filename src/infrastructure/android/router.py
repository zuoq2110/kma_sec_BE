import token
from typing import Annotated,Optional
from httpx import AsyncClient
from fastapi import APIRouter, Depends, UploadFile, HTTPException, status, Request
from .service import AndroidService
from src.data.local.source.user import oauth2_scheme
from fastapi.responses import StreamingResponse
import httpx

router = APIRouter(prefix="/android", tags=["android"])


async def get_token(request: Request):
    token = request.headers.get("Authorization")
    if token and token.startswith("Bearer "):
        return token[7:]  # Trả về token mà không có "Bearer "
    return None  # Nếu không có token, trả về None

@router.post(path="/applications", status_code=status.HTTP_201_CREATED)
async def create_analysis(
    file: UploadFile,
    service: Annotated[AndroidService, Depends()],
    token:Optional[str] = Depends(get_token),
):
    try:
        analysis_id = await service.create_analysis(file=file,token=token if token else None)
        
        # # Gửi file đến đường dẫn mới
        # async with AsyncClient() as client:
        #     response = await client.post(
        #         "http://192.168.1.103:8086/upload",
        #         files={"file": (file.filename, await file.read(), file.content_type)},
        #         data={"web_name": "KMA_SEC"}
        #     )

        # # Kiểm tra phản hồi từ server
        # response.raise_for_status()  # Raise an exception for HTTP errors
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
    service: Annotated[AndroidService, Depends()],
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
    service: Annotated[AndroidService, Depends()]
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

@router.get("/download")
async def download_file(file_name: str, web_name: str):
    try:
        async with httpx.AsyncClient() as client:
            # Gọi API tải xuống từ máy chủ khác
            response = await client.get("http://192.168.1.103:8086/download", params={"file_name": file_name, "web_name": web_name})

            # Kiểm tra mã trạng thái của phản hồi
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            # Trả về dữ liệu tải xuống cho người dùng
            return StreamingResponse(response.iter_content(), media_type='application/octet-stream', headers={
                "Content-Disposition": f"attachment; filename={file_name}"
            })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"There was an error: {str(e)}")