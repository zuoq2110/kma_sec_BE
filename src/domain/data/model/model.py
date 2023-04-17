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
    output: list[str]
    accuracy: float
    loss: float
    precision: float
    recall: float
    f1: float
    created_at: str


@dataclass
class ModelHistory:
    accuracy: list[float]
    val_accuracy: list[float]
    loss: list[float]
    val_loss: list[float]
