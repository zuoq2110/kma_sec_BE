from dataclasses import dataclass


@dataclass
class AndroidApplication:
    id: str
    name: str
    package: str
    version_code: int
    version_name: str
    malware_type: str
    created_at: str


@dataclass
class AndroidApplicationDetails:
    id: str
    name: str
    package: str
    version_code: int
    version_name: str
    user_features: list[str]
    permissions: list[str]
    activities: list[str]
    services: list[str]
    receivers: list[str]
    malware_type: str
    created_at: str
