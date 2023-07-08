from typing import Annotated, Optional
from fastapi import Depends
from src.data.util import analyze
from src.domain.data.model.model import MODEL_INPUT_FORMAT_PE
from .model import ModelRepository


class WindowsApplicationRepository:

    def __init__(self, model_repository: Annotated[ModelRepository, Depends()]):
        self._model_repository = model_repository

    async def create_application_analysis(self, raw: bytes) -> dict:
        analysis = await analyze(raw=raw)

        analysis["malware_type"] = await self._get_application_malware_type(analysis=analysis)
        return analysis

    async def _get_application_malware_type(self, analysis: dict) -> Optional[str]:
        models = await self._model_repository.get_models(input_format=MODEL_INPUT_FORMAT_PE, limit=1)

        if not models:
            return None

        # Load model

        # Pre-processing

        # Run model prediction with the input data.

        return "Benign"

    async def get_application_analysis(self, analysis_id: str) -> Optional[dict]:
        return None
