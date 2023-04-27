from typing import Optional
from pefile import PE
from src.data.util import extract
from src.domain.util import InvalidArgumentException


class WindowsApplicationRepository:

    async def create_application_analysis(self, pe_bytes: bytes) -> dict:
        try:
            pe = PE(data=pe_bytes)
        except:
            raise InvalidArgumentException("Invalid attachment! Only PE format is supported.")

        analytic = extract(pe=pe)
        return analytic

    async def get_application_analysis(self, analysis_id: str) -> Optional[dict]:
        return None
