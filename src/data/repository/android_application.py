import numpy as np

from typing import Annotated, Optional
from os import sep
from os.path import join
from bson import ObjectId
from fastapi import Depends
from androguard.core.bytecodes.apk import APK
from keras.models import load_model
from src.domain.data.model import AndroidApplicationDetails
from src.domain.data.model.model import MODEL_INPUT_FORMAT_APK, MODEL_SOURCE_TYPE_HDF5
from src.domain.util import InvalidArgumentException
from src.data.local import AndroidApplicationLocalDataSource
from src.data.util import get_metadata, disassamble, async_generator
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

    async def create_application_analysis(self, apk_bytes: bytes) -> str:
        try:
            apk = APK(apk_bytes, raw=True)
        except:
            raise InvalidArgumentException("Invalid attachment! Only APK format is supported.")

        package = apk.get_package()
        document = await self._local_data_source.find_by_package(package=package)

        if document != None:
            return str(object=document["_id"])

        metadata = get_metadata(apk=apk)
        report = await disassamble(apk_bytes=apk_bytes, cache_dir=join(sep, "data", "cache"))
        apis = list(report['apis'])

        if not apis:
            raise InvalidArgumentException("Invalid attachment! Can't parse APK file.")

        malware_type = await self._get_application_malware_type(permissions=metadata["permissions"], apis=apis)
        document_id = await self._local_data_source.insert(metadata=metadata, malware_type=malware_type)

        await self._android_application_api_repository.create_application_apis(application_id=document_id, apis=apis)
        return str(object=document_id)

    async def _get_application_malware_type(self, permissions: list, apis: list) -> Optional[str]:
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

        x = np.array(object=[buffer])
        x = np.concatenate((x, np.zeros((x.shape[0], 15))), 1)
        x = x.reshape(x.shape[0], 44, 44, 1)

        # Run model prediction with the input data.
        y = model(x)[0]
        y = list(y)

        # Post-processing: find the digit that has the highest probability
        model_output = model_details.output
        highest_probability = max(y)
        index = y.index(highest_probability)

        return model_output[index]

    async def get_application_analysis(self, analysis_id: str) -> Optional[AndroidApplicationDetails]:
        id = ObjectId(oid=analysis_id)
        document = await self._local_data_source.find_by_id(document_id=id)

        if document == None:
            return None

        return self._as_android_application_details(document=document)

    def _as_android_application_details(self, document) -> AndroidApplicationDetails:
        return AndroidApplicationDetails(
            id=str(object=document['_id']),
            name=document['name'],
            package=document['package'],
            version_code=document['version_code'],
            version_name=document['version_name'],
            user_features=document['user_features'],
            permissions=document['permissions'],
            activities=document['activities'],
            services=document['services'],
            receivers=document['receivers'],
            malware_type=document['malware_type']
        )
