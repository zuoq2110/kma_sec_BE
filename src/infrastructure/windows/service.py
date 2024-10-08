from typing import Annotated
from fastapi import Depends, UploadFile, HTTPException, status
from src.data import WindowsApplicationRepository
from src.domain.util import InvalidArgumentException
from src.data.local.source.user import oauth2_scheme
from typing import Optional


class WindowsService:

    def __init__(self, windows_application_respository: Annotated[WindowsApplicationRepository, Depends()]):
        self._windows_application_respository = windows_application_respository

    async def create_application_analysis(self, file: UploadFile, token:Optional[str] = Depends(oauth2_scheme)):
        raw = await file.read()
        try:
            analysis_id = await self._windows_application_respository.create_application_analysis(raw=raw, token=token if token else None)
        except InvalidArgumentException as exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(object=exception)
            )

        return analysis_id

    async def get_analyses(self, page: int = 1, limit: int = 20):
        return await self._windows_application_respository.get_analyses(page=page, limit=limit)

    async def get_analysis_details(self, analysis_id: str):
        analysis = await self._windows_application_respository.get_analysis_details(analysis_id=analysis_id)

        if analysis == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Windows application analysis details could not be found!"
            )

        return analysis
