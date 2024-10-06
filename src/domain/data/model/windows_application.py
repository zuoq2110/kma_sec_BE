from dataclasses import dataclass
from typing import Optional


@dataclass
class WindowsApplication:
    id: str
    md5: str
    malware_type: str
    created_at: str
    created_by: Optional[str] = None


@dataclass
class WindowsApplicationDetails:
    id: str
    md5: str
    dos_header: dict
    header_characteristics: int
    header: dict
    optional_header: dict
    data_directories: list
    sections: list
    _import: Optional[dict]
    libraries: list
    tls: Optional[dict]
    malware_type: str
    created_at: str
