import numpy as np

from os import sep
from os.path import join
from typing import Annotated, Optional
from fastapi import Depends
from pefile import PE
from keras.models import load_model
from src.data.util import extract
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
        # Load model
        model_id = "644a35532a59a202605f6038"
        model_source = join(sep, "data", "files", model_id, "model.h5")
        model = load_model(filepath=model_source)

        INPUT_SIZE = 9

        # Pre-processing
        data = pe_analytic.copy()

        for key in ['MD5', 'SHA-1', 'SHA-256', 'SHA-512']:
            data.pop(key)

        buffer = [pe_analytic[key] for key in data]
        x = np.array(object=[buffer])
        x = np.nan_to_num(x=x, nan=0)
        x = x / np.max(x, axis=0)
        x = np.concatenate((x, np.zeros((x.shape[0], 5))), 1)
        x = x.reshape(x.shape[0], INPUT_SIZE, INPUT_SIZE, 1)

        # Run model prediction with the input data.
        y = model(x)[0]
        y = list(y)

        # Post-processing: find the digit that has the highest probability
        model_output = ["Benign", "Malware"]
        highest_probability = max(y)
        index = y.index(highest_probability)

        return model_output[index]

    async def get_application_analysis(self, analysis_id: str) -> Optional[dict]:
        return None
