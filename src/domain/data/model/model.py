from dataclasses import dataclass


MODEL_TYPE_HDF5 = 'HDF5/H5'
MODEL_TYPE_PICKLE = 'PICKLE'

MODEL_INPUT_FORMAT_APK = "APK"
MODEL_INPUT_FORMAT_PE = "PE"

MODEL_SOURCE_TYPE_HDF5 = "h5"
MODEL_SOURCE_TYPE_TFLITE = "tflite"
MODEL_SOURCE_TYPE_PICKLE = "pickle"


@dataclass
class Model:
    id: str
    version: str
    type: str
    input_format: str
    created_at: str


@dataclass
class ModelDetails:
    id: str
    version: str
    type: str
    size: int
    input_format: str
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
