import numpy as np

from typing import Annotated, Optional
from fastapi import Depends
from pefile import PE
from pickle import load
from src.data.util import extract, async_generator
from src.domain.data.model.model import MODEL_INPUT_FORMAT_PE, MODEL_SOURCE_TYPE_PICKLE
from src.domain.util import InvalidArgumentException
from .model import ModelRepository


class WindowsApplicationRepository:

    def __init__(self, model_repository: Annotated[ModelRepository, Depends()]):
        self._model_repository = model_repository

    async def create_application_analysis(self, pe_bytes: bytes) -> dict:
        try:
            pe = PE(data=pe_bytes)
        except:
            raise InvalidArgumentException("Invalid attachment! Only PE format is supported.")

        analytic = extract(pe=pe)
        analytic["malware_type"] = await self._get_application_malware_type(pe_analytic=analytic)
        return analytic

    async def _get_application_malware_type(self, pe_analytic: dict) -> Optional[str]:
        models = await self._model_repository.get_models(input_format=MODEL_INPUT_FORMAT_PE, limit=1)

        if not models:
            return None

        # Load model
        model_id = models[0].id
        model_source = await self._model_repository.get_model_source(model_id=model_id, format=MODEL_SOURCE_TYPE_PICKLE)

        with open(file=model_source, mode='rb') as file:
            model = load(file=file)

        # Pre-processing
        model_input = await self._model_repository.get_model_input(model_id=model_id)
        size = len(model_input)
        buffer = [0] * size

        async for i in async_generator(data=range(size)):
            key = model_input[i]
            try:
                buffer[i] = pe_analytic[key]
            except:
                pass
        x = np.array(object=[buffer])
        x = np.nan_to_num(x=x, nan=0)

        # Run model prediction with the input data.
        y = model.predict(x)[0]

        # Post-processing:
        model_details = await self._model_repository.get_model_details(model_id=model_id)
        model_output = model_details.output
        result = model_output[y]
        return result

    async def get_application_analysis(self, analysis_id: str) -> Optional[dict]:
        return None
