import numpy as np

from typing import Annotated, Optional
from os import sep, environ
from os.path import join
from fastapi import Depends
from bson import ObjectId
from keras.models import load_model
from pandas import read_csv
from src.domain.data.model import WindowsApplicationDetails
from src.domain.data.model.model import ModelInputFormat, ModelState, ModelSourceFormat
from src.data.local import WindowsApplicationLocalDataSource
from src.data.local.document import as_windows_application, as_windows_application_details
from src.data.util import analyze, normalize
from .model import ModelRepository

# Configure the Tensorflow logging module
environ['TF_CPP_MIN_LOG_LEVEL'] = '1'


class WindowsApplicationRepository:

    def __init__(
        self, 
        local_data_source: Annotated[WindowsApplicationLocalDataSource, Depends()],
        model_repository: Annotated[ModelRepository, Depends()]
    ):
        self.__local_data_source = local_data_source
        self.__model_repository = model_repository

    async def create_application_analysis(self, raw: bytes, token: Optional[str]) -> dict:
        analysis = await analyze(raw=raw)
        document = await self.__local_data_source.find_by_md5(
                md5=analysis["md5"],
                token=token
            )
        if document is not None:
                print("abc")
                return str(object=document["_id"])

        malware_type = await self.__get_application_malware_type(analysis=analysis)
        document_id = await self.__local_data_source.insert(metadata=analysis, malware_type=malware_type, token=token if token else None)

        return str(object=document_id)

    async def __get_application_malware_type(self, analysis: dict) -> Optional[str]:
        models = await self.__model_repository.get_models(
            input_format=ModelInputFormat.PE,
            state=ModelState.ACTIVATE,
            limit=1
        )

        if not models:
            return None

        # # Load model
        model_id = models[0].id
        model_details = await self.__model_repository.get_model_details(model_id=model_id)
        model_source = await self.__model_repository.get_model_source(model_id=model_id, format=ModelSourceFormat.HDF5)
        model = load_model(filepath=model_source)

        # Pre-processing
        # x = normalize(analysis=analysis)
        x = await normalize(analysis=analysis)
        x = [0 if elem is None else elem for elem in x]

        thresholds = self.__get_thresholds(model_id=model_id)
        x = np.array(object= x)
        # x = np.divide(x, thresholds, where=thresholds!=0, out=np.full_like(x, 0))
        
        if x is None:
            raise ValueError("Variable 'x' should not be None.")
        
        if thresholds is None:
            raise ValueError("Variable 'thresholds' should not be None.")


        if x is not None and thresholds is not None:
            x = np.divide(x, thresholds, where=thresholds != 0, out=np.full_like(x, 0))
        else:
    # Xử lý tình huống khi một trong hai giá trị là None
            x = np.full_like(x, 0)  # Hoặc thực hiện một hành động khác phù hợp

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
        thresholds_path = join("E:","\Code","serverkma-sec","server", ".docker", "data", "files", "models", model_id, "thresholds.csv")
        thresholds = read_csv(filepath_or_buffer=thresholds_path)["threshold"]
        thresholds = np.array(object=thresholds)

        return thresholds

    async def get_analyses(self, page: int = 1, limit: int = 20) -> list:
        cursor = await self.__local_data_source.find_all(page=page, limit=limit)
        analyses = [as_windows_application(document=document) for document in cursor]
        print(analyses)
        return analyses

    async def get_analysis_details(self, analysis_id: str) -> Optional[WindowsApplicationDetails]:
        id = ObjectId(oid=analysis_id)
        document = await self.__local_data_source.find_by_id(document_id=id)

        return None if document is None else as_windows_application_details(document=document)
