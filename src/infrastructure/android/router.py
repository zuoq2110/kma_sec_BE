import token
from typing import Annotated,Optional
from httpx import AsyncClient
from fastapi import APIRouter, Depends, UploadFile, HTTPException, status, Request
from .service import AndroidService
from src.data.local.source.user import oauth2_scheme
from fastapi.responses import StreamingResponse
import httpx
from ..util.jwtService import get_token

router = APIRouter(prefix="/android", tags=["android"])




@router.post(path="/applications", status_code=status.HTTP_201_CREATED)
async def create_analysis(
    file: UploadFile,
    service: Annotated[AndroidService, Depends()],
    token:Optional[str] = Depends(get_token),
):
    try:
        analysis_id = await service.create_analysis(file=file,token=token if token else None)
        
        # Gửi file đến đường dẫn mới
        # async with AsyncClient() as client:
        #     response = await client.post(
        #         "http://192.168.1.103:8086/upload",
        #         files={"file": (file.filename, await file.read(), file.content_type)},
        #         data={"web_name": "KMA_SEC"}
        #     )
        #     print(response)

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

# @router.post(path="/applications", status_code=status.HTTP_201_CREATED)
# async def create_analysis(
#     file: UploadFile,
#     service: Annotated[AndroidService, Depends()],
#     token: Optional[str] = Depends(get_token),
# ):
#     try:
        
#         file_content = await file.read()

#         # Tạo phân tích
#         analysis_id = await service.create_analysis(file=file, token=token if token else None)

#         # Gửi file APK đến server
#         async with AsyncClient() as client:
#             response = await client.post(
#                 "http://192.168.1.103:8086/upload",
#                 files={"file": (file.filename, file_content, "application/vnd.android.package-archive")},
#                 data={"web_name": "KMA_SEC"}
#             )

#         # Kiểm tra phản hồi từ server
#         print(response)
#         response.raise_for_status()  # Raise an exception for HTTP errors
#         print("abc")

#         # Kiểm tra xem server có trả về thông báo thành công không
#         if response.status_code != 200 or "success" not in response.json():
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail="Failed to upload APK to server."
#             )

#     except HTTPException as http_exc:
#         raise http_exc
#     except Exception as exception:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=str(exception)
#         )

#     return {
#         "message": "Create an Android application's analysis and uploaded APK successfully.",
#         "data": {"analysis_id": analysis_id}
#     }


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

# @router.get("/download")
# async def download_file(file_name: str, web_name: str):
#     try:
#         async with httpx.AsyncClient() as client:
#             # Gọi API tải xuống từ máy chủ khác
#             response = await client.get("http://192.168.1.103:8086/download1", params={"file_name": file_name, "web_name": web_name})
#             print(response)
#             # Kiểm tra mã trạng thái của phản hồi
#             if response.status_code != 200:
#                 raise HTTPException(status_code=response.status_code, detail=response.text)

#             # Trả về dữ liệu tải xuống cho người dùng
#             return StreamingResponse(response.iter_content(), media_type='application/octet-stream', headers={
#                 "Content-Disposition": f"attachment; filename={file_name}"
#             })

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"There was an error: {str(e)}")

# @router.get("/download")
# async def download_file(file_name: str, web_name: str):
#     try:
#         async with httpx.AsyncClient() as client:
#             # Gọi API tải xuống từ máy chủ khác
#             response = await client.get(
#                 "http://192.168.1.103:8086/download1", 
#                 params={"file_name": file_name, "web_name": web_name}
#             )
            
#             # Kiểm tra mã trạng thái của phản hồi
#             if response.status_code != 200:
#                 raise HTTPException(status_code=response.status_code, detail=response.text)

#             # Trả về dữ liệu tải xuống cho người dùng
#             return StreamingResponse(
#                 iter(response.content),  # Sử dụng content để trả về toàn bộ dữ liệu
#                 media_type='application/octet-stream',
#                 headers={
#                     "Content-Disposition": f"attachment; filename={file_name}"
#                 }
#             )

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"There was an error: {str(e)}")


@router.get("/download")
async def download_file(file_name: str, web_name: str):
    try:
        # Đường dẫn của server mà bạn muốn tải file từ đó
        download_url = "http://192.168.1.103:8086/download1"

        async with httpx.AsyncClient() as client:
            # Gọi API tải xuống từ máy chủ khác
            response = await client.get(download_url, params={"file_name": file_name, "web_name": web_name})
            print("Response:", response)
            
            # Kiểm tra mã trạng thái của phản hồi
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            # Trả về dữ liệu tải xuống cho người dùng
            return StreamingResponse(
                iter([response.content]),  # Trả về iterator cho content
                media_type='application/octet-stream',
                headers={
                    "Content-Disposition": f"attachment; filename={file_name}"
                }
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"There was an error: {str(e)}")