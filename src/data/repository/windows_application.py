import numpy as np

from os import sep
from os.path import join
from typing import Annotated, Optional
from fastapi import Depends
from pefile import PE
from keras.models import load_model
from src.data.util import extract, async_generator
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
        model_input = [
            'e_magic', 'e_cblp', 'e_cp', 'e_crlc', 'e_cparhdr', 'e_minalloc', 'e_maxalloc', 'e_ss', 'e_sp',
            'e_csum', 'e_ip', 'e_cs', 'e_lfarlc', 'e_ovno', 'e_oemid', 'e_oeminfo', 'e_lfanew', 'Machine',
            'SizeOfOptionalHeader', 'Characteristics', 'Signature', 'Magic', 'MajorLinkerVersion',
            'MinorLinkerVersion', 'SizeOfCode', 'SizeOfInitializedData', 'SizeOfUninitializedData',
            'AddressOfEntryPoint', 'BaseOfCode', 'BaseOfData', 'ImageBase', 'SectionAlignment',
            'FileAlignment', 'MajorOperatingSystemVersion', 'MinorOperatingSystemVersion',
            'MajorImageVersion', 'MinorImageVersion', 'MajorSubsystemVersion', 'MinorSubsystemVersion',
            'Reserved1', 'SizeOfImage', 'SizeOfHeaders', 'CheckSum', 'Subsystem', 'DllCharacteristics',
            'SizeOfStackReserve', 'SizeOfStackCommit', 'SizeOfHeapReserve', 'SizeOfHeapCommit', 'LoaderFlags',
            'NumberOfRvaAndSizes', 'LengthOfPeSections', 'MeanEntropy', 'MinEntropy', 'MaxEntropy',
            'MeanRawSize', 'MinRawSize', 'MaxRawSize', 'MeanVirtualSize', 'MinVirtualSize', 'MaxVirtualSize',
            'ImportsNbDLL', 'ImportsNb', 'ImportsNbOrdinal', 'ExportNb', 'ResourcesMeanEntropy',
            'ResourcesMinEntropy', 'ResourcesMaxEntropy', 'ResourcesMeanSize', 'ResourcesMinSize',
            'ResourcesMaxSize', 'ResourcesNb', 'LoadConfigurationSize', 'VersionInformationSize', 'DLL',
            'LengthOfInformation'
        ]
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
