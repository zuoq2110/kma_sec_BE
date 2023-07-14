from dataclasses import dataclass
from enum import Enum


MODEL_SOURCE_TYPE_HDF5 = "h5"
MODEL_SOURCE_TYPE_TFLITE = "tflite"
MODEL_SOURCE_TYPE_PICKLE = "pickle"


class ModelType(Enum):
    HDF5 = "HDF5/H5"
    PICKLE = "PICKLE"


class ModelInputFormat(Enum):
    APK = "APK"
    PE = "PE"


class ModelState(Enum):
    TRAINING = "Training"
    DEACTIVATE = "Deactivate"
    ACTIVATE = "Activate"


@dataclass
class Model:
    id: str
    version: str
    type: ModelType
    input_format: ModelInputFormat
    state: ModelState
    created_at: str


@dataclass
class ModelDetails:
    id: str
    version: str
    type: ModelType
    input_format: ModelInputFormat
    state: ModelState
    size: int
    output: list[str]
    accuracy: float
    precision: float
    recall: float
    f1: float
    created_at: str


@dataclass
class ModelDataset:
    label: str
    quantity: int


@dataclass
class ModelHistory:
    accuracy: list[float]
    val_accuracy: list[float]
    loss: list[float]
    val_loss: list[float]
