import numpy as np

from typing import Annotated, Optional
from os import sep, environ
from os.path import join
from fastapi import Depends
from keras.models import load_model
from pandas import read_csv
from src.domain.data.model.model import MODEL_INPUT_FORMAT_PE, MODEL_SOURCE_TYPE_HDF5, ModelState
from src.data.util import analyze, normalize
from .model import ModelRepository

# Configure the Tensorflow logging module
environ['TF_CPP_MIN_LOG_LEVEL'] = '1'


class WindowsApplicationRepository:

    def __init__(self, model_repository: Annotated[ModelRepository, Depends()]):
        self.__model_repository = model_repository

    async def create_application_analysis(self, raw: bytes) -> dict:
        analysis = await analyze(raw=raw)

        analysis["malware_type"] = await self.__get_application_malware_type(analysis=analysis)
        return analysis

    async def __get_application_malware_type(self, analysis: dict) -> Optional[str]:
        models = await self.__model_repository.get_models(
            input_format=MODEL_INPUT_FORMAT_PE,
            state=ModelState.ACTIVATE,
            limit=1
        )

        if not models:
            return None

        # # Load model
        model_id = models[0].id
        model_details = await self.__model_repository.get_model_details(model_id=model_id)
        model_source = await self.__model_repository.get_model_source(model_id=model_id, format=MODEL_SOURCE_TYPE_HDF5)
        model = load_model(filepath=model_source)

        # Pre-processing
        x = normalize(analysis=analysis)

        thresholds = self.__get_thresholds(model_id=model_id)
        x = np.array(object=await x)
        x = np.divide(x, thresholds, where=thresholds!=0, out=np.full_like(x, 0))

        # Transform vector input to an 2D array (44x44)
        matrix_size = 27
        padding_size = matrix_size * matrix_size - x.size
        x = np.array(object=[x])
        x = np.concatenate((x, np.zeros((x.shape[0], padding_size))), 1)
        x = x.reshape(x.shape[0], matrix_size, matrix_size, 1)

        # # Run model prediction with the input data.
        y = model(x)[0]
        y = list(y)

        # # Post-processing: find the digit that has the highest probability
        model_output = model_details.output
        highest_probability = max(y)
        index = y.index(highest_probability)

        return model_output[index]

    def __get_thresholds(self, model_id: str):
        thresholds_path = join(sep, "data", "files",model_id, "thresholds.csv")
        thresholds = read_csv(filepath_or_buffer=thresholds_path)["threshold"]
        thresholds = np.array(object=thresholds)

        return thresholds

    async def get_application_analysis(self, analysis_id: str) -> Optional[dict]:
        return None
