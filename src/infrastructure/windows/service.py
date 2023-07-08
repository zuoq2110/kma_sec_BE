from typing import Annotated
from fastapi import Depends, UploadFile, HTTPException, status
from src.data import WindowsApplicationRepository
from src.domain.util import InvalidArgumentException


class WindowsService:

    def __init__(self, windows_application_respository: Annotated[WindowsApplicationRepository, Depends()]):
        self._windows_application_respository = windows_application_respository

    async def create_application_analysis(self, file: UploadFile):
        raw = await file.read()
        try:
            analysis = await self._windows_application_respository.create_application_analysis(raw=raw)
        except InvalidArgumentException as exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(object=exception)
            )

        return analysis

    async def get_application_analysis_details(self, analysis_id: str):
        analysis = await self._windows_application_respository.get_application_analysis(analysis_id=analysis_id)

        if analysis == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Windows application analysis details could not be found!"
            )

        return analysis
