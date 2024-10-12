from typing import Annotated, Optional

from fastapi import Depends, UploadFile, HTTPException, status

from src.data import PdfApplicationRepository
from src.data.local.source.user import oauth2_scheme
from src.domain.util import InvalidArgumentException


class PdfService:

    def __init__(self, pdf_application_respository: Annotated[PdfApplicationRepository, Depends()]):
        self._pdf_application_respository = pdf_application_respository

    async def create_analysis(self,  file: UploadFile, token:Optional[str] = Depends(oauth2_scheme)):
        try:
            analysis_id = await self._pdf_application_respository.create_application_analysis(file=file, token=token if token else None)
        except InvalidArgumentException as exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(object=exception)
            )
        print("analysis_id",analysis_id)
        return analysis_id

    async def get_analysis(self, page: int = 1, limit: int = 20):
        return await self._pdf_application_respository.get_analyses(page=page, limit=limit)

    async def get_analysis_details(self, analysis_id: str):
        analysis = await self._pdf_application_respository.get_analysis_details(analysis_id=analysis_id)

        if analysis == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Windows application analysis details could not be found!"
            )

        return analysis
