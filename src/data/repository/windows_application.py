import numpy as np

from os import sep
from os.path import join
from typing import Optional
from pefile import PE
from pickle import load
from src.data.util import extract, async_generator
from src.domain.util import InvalidArgumentException


class WindowsApplicationRepository:

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
        model = self._get_model(model_id=model_id)

        # Pre-processing
        model_input = [
            'e_magic', 'e_cblp', 'e_cp', 'e_crlc', 'e_cparhdr', 'e_minalloc', 'e_maxalloc', 'e_ss', 
            'e_sp', 'e_csum', 'e_ip', 'e_cs', 'e_lfarlc', 'e_ovno', 'e_oemid', 'e_oeminfo', 
            'e_lfanew', 'Machine', 'SizeOfOptionalHeader', 'Characteristics', 'Signature', 
            'Magic', 'MajorLinkerVersion', 'MinorLinkerVersion', 'SizeOfCode', 
            'SizeOfInitializedData', 'SizeOfUninitializedData', 'AddressOfEntryPoint', 'BaseOfCode', 
            'BaseOfData', 'ImageBase', 'SectionAlignment', 'FileAlignment', 
            'MajorOperatingSystemVersion', 'MinorOperatingSystemVersion', 'MajorImageVersion', 
            'MinorImageVersion', 'MajorSubsystemVersion', 'MinorSubsystemVersion', 'Reserved1', 
            'SizeOfImage', 'SizeOfHeaders', 'CheckSum', 'Subsystem', 'DllCharacteristics', 
            'SizeOfStackReserve', 'SizeOfStackCommit', 'SizeOfHeapReserve', 'SizeOfHeapCommit', 
            'LoaderFlags', 'NumberOfRvaAndSizes', 'LengthOfPeSections', 'MeanRawSize', 
            'MeanVirtualSize', 'ImportsNbDLL', 'ImportsNbOrdinal'
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

        # Run model prediction with the input data.
        y = model.predict(x)[0]

        # Post-processing:
        model_output = [
            "Benign", "Virus", "Trojan", "Adware", "Worm", "Pua", "Downloader", "Ransomware", 
            "Hacktool", "Miner", "Banker", "No Label", "Dropper", "Fakeav", "Suspack", "Damaged"
        ]
        result = model_output[y]
        return result

    def _get_model(self, model_id: str):
        model_source = join(sep, "data", "files", model_id, "model.pickle")

        with open(file=model_source, mode='rb') as file:
            model = load(file=file)
        return model

    async def get_application_analysis(self, analysis_id: str) -> Optional[dict]:
        return None
