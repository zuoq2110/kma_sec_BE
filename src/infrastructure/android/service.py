from typing import Annotated
from fastapi import Depends, UploadFile
from src.data import AndroidApplicationRepository


class AndroidService:

    def __init__(self, android_application_respository: Annotated[AndroidApplicationRepository, Depends()]):
        self._android_application_respository = android_application_respository

    async def create_application_analysis(self, file: UploadFile):
        bytes = await file.read()

        return await self._android_application_respository.create_application_analysis(apk_bytes=bytes)

    async def get_application_analysis(self, page: int = 1, limit: int = 20):
        return await self._android_application_respository.get_application_analysis(page=page, limit=limit)

    async def get_application_analysis_details(self, analysis_id: str):
        return await self._android_application_respository.get_application_analysis_details(analysis_id=analysis_id)
