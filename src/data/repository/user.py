import numpy as np

from typing import Annotated, Optional
from os import environ
from bson import ObjectId
from fastapi import Depends
from androguard.core.bytecodes.apk import APK
from keras.models import load_model
from src.domain.data.model import AndroidApplicationDetails
from src.domain.data.model.model import ModelInputFormat, ModelState, ModelSourceFormat
from src.domain.util import InvalidArgumentException
from src.data.local import AndroidApplicationLocalDataSource
from src.data.local.document import as_android_application, as_android_application_details
from src.data.util import get_metadata, get_apis, async_generator
from .model import ModelRepository
from .android_application_api import AndroidApplicationApiRepository
from src.data.local import UserLocalDataSource
from src.data.local.source.user import UserCreate

class UserRepository:

    def __init__(
        self,
        local_data_source: Annotated[UserLocalDataSource, Depends()]
    ):
        self._local_data_source = local_data_source

    async def create_user(self, user ):
        return await self._local_data_source.insert(user)
    
    async def find_user(self, id):
        result = await self._local_data_source.find_one(id=id)
        return result
  
    