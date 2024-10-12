from dataclasses import dataclass
from typing import Optional


@dataclass
class PdfApplication:
    id: str
    name: str
    malware_type: str
    created_at: str
    created_by: Optional[str] = None

@dataclass
class PdfApplicationDetails:
    id: str
    name:str
    attributes: dict
    malware_type: str
    created_at: str
    created_by: Optional[str] = None