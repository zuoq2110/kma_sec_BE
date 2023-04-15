from typing import Annotated
from fastapi import Depends, UploadFile, HTTPException, status
from src.data import AndroidApplicationRepository
from src.domain.util import InvalidArgumentException

CONTENT_TYPE_APK = "application/vnd.android.package-archive"


class AndroidService:

    def __init__(self, android_application_respository: Annotated[AndroidApplicationRepository, Depends()]):
        self._android_application_respository = android_application_respository

    async def create_application_analysis(self, file: UploadFile):
        if file.content_type != CONTENT_TYPE_APK:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid attachment! Only APK format is supported."
            )

        bytes = await file.read()
        try:
            analysis_id = await self._android_application_respository.create_application_analysis(apk_bytes=bytes)
        except InvalidArgumentException as exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=str(object=exception)
            )

        return analysis_id

    async def get_application_analysis_details(self, analysis_id: str):
        analysis = await self._android_application_respository.get_application_analysis(analysis_id=analysis_id)

        if analysis == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Android application analysis details could not be found!"
            )

        return analysis
