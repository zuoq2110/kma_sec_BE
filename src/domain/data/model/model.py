from dataclasses import dataclass


@dataclass
class Model:
    id: str
    version: str
    type: str
    created_at: str


@dataclass
class ModelDetails:
    id: str
    version: str
    type: str
    size: int
    input: list[str]
    output: list[str]
    accuracy: float
    loss: float
    precision: float
    recall: float
    f1: float
    history: dict
    created_at: str
