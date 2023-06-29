import numpy as np

from typing import Annotated, Optional
from bson import ObjectId
from fastapi import Depends
from androguard.core.bytecodes.apk import APK
from keras.models import load_model
from src.domain.data.model import AndroidApplicationDetails
from src.domain.data.model.model import MODEL_INPUT_FORMAT_APK, MODEL_SOURCE_TYPE_HDF5
from src.domain.util import InvalidArgumentException
from src.data.local import AndroidApplicationLocalDataSource
from src.data.local.document import as_android_application, as_android_application_details
from src.data.util import get_metadata, get_apis, async_generator
from .model import ModelRepository
from .android_application_api import AndroidApplicationApiRepository


class AndroidApplicationRepository:

    def __init__(
        self,
        local_data_source: Annotated[AndroidApplicationLocalDataSource, Depends()],
        model_repository: Annotated[ModelRepository, Depends()],
        android_application_api_repository: Annotated[AndroidApplicationApiRepository, Depends()]
    ):
        self._local_data_source = local_data_source
        self._model_repository = model_repository
        self._android_application_api_repository = android_application_api_repository

    async def create_analysis(self, apk_bytes: bytes) -> str:
        try:
            apk = APK(apk_bytes, raw=True)
        except:
            raise InvalidArgumentException("Invalid attachment! Only APK format is supported.")

        metadata = await get_metadata(apk=apk)

        if metadata["certificates"]:
            document = await self._local_data_source.find_by_certificate(certificate=metadata["certificates"][0])

            if document is not None:
                return str(object=document["_id"])

        apis = await get_apis(apk=apk)

        if not apis:
            raise InvalidArgumentException("Invalid attachment! Can't parse APK file.")

        malware_type = await self._get_malware_type(permissions=metadata["permissions"], apis=apis)
        document_id = await self._local_data_source.insert(metadata=metadata, malware_type=malware_type)

        await self._android_application_api_repository.create_application_apis(application_id=document_id, apis=apis)
        return str(object=document_id)

    async def _get_malware_type(self, permissions: list, apis: list) -> Optional[str]:
        models = await self._model_repository.get_models(input_format=MODEL_INPUT_FORMAT_APK, limit=1)

        if not models:
            return None

        # Load model
        model_id = models[0].id
        model_details = await self._model_repository.get_model_details(model_id=model_id)
        model_source = await self._model_repository.get_model_source(model_id=model_id, format=MODEL_SOURCE_TYPE_HDF5)
        model = load_model(filepath=model_source)

        # Pre-processing
        model_input = await self._model_repository.get_model_input(model_id=model_id)
        permissions = [permission.split(".")[-1].upper() async for permission in async_generator(permissions)]
        size = len(model_input)
        buffer = [0] * size

        async for i in async_generator(data=range(size)):
            label = model_input[i]
            buffer[i] = 1 if label in permissions or label in apis else 0

        matrix_size = 44
        padding_size = matrix_size * matrix_size - size
        x = np.array(object=[buffer])
        x = np.concatenate((x, np.zeros((x.shape[0], padding_size))), 1)
        x = x.reshape(x.shape[0], matrix_size, matrix_size, 1)

        # Run model prediction with the input data.
        y = model(x)[0]
        y = list(y)

        # Post-processing: find the digit that has the highest probability
        model_output = model_details.output
        highest_probability = max(y)
        index = y.index(highest_probability)

        return model_output[index]

    async def get_analysis(self, page: int = 1, limit: int = 20) -> list:
        cursor = await self._local_data_source.find_all(page=page, limit=limit)
        analysis = [as_android_application(document=document) for document in cursor]

        return analysis

    async def get_analysis_details(self, analysis_id: str) -> Optional[AndroidApplicationDetails]:
        id = ObjectId(oid=analysis_id)
        document = await self._local_data_source.find_by_id(document_id=id)

        return None if document is None else as_android_application_details(document=document)
