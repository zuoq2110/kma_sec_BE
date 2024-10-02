import numpy as np

from os import sep
from os.path import join
from androguard.core.bytecodes.apk import APK
from keras.utils import to_categorical
from keras.models import load_model, Sequential
from pandas import read_csv
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from src.data.util import async_generator, get_metadata, get_apis


async def train(
    source: str,
    input: list,
    output: list,
    dataset: list,
    epochs: int
):
    analyses = await __analyze(dataset=dataset)
    y, x = await __normalize(analyses=analyses, model_input=input, model_output=output)
    val_y, val_x = __get_validate_dataset()
    model: Sequential = load_model(filepath=source)
    history = model.fit(
        x=x,
        y=y,
        batch_size=16,
        epochs=epochs,
        verbose=0,
        validation_data=(val_x, val_y)
    )
    report = __evaluate(model=model)

    return model, history, report


async def __analyze(dataset: list) -> list:
    analyses = []

    async for file in async_generator(data=dataset):
        bytes = file["content"]
        apk = APK(bytes, raw=True)
        metadata = get_metadata(apk=apk)
        apis = get_apis(apk=apk)
        analysis = {}

        analysis.update(await metadata)
        analysis["apis"] = await apis
        analysis["type"] = file["label"]
        analyses.append(analysis)
    return analyses


async def __normalize(analyses: list, model_input: list[str], model_output: list[str]):
    X = []
    Y = []

    output = [None if label is None else label.lower() for label in model_output]
    input_size = len(model_input)

    async for analysis in async_generator(data=analyses):
        permissions = await __normalize_permissions(permissions=analysis["permissions"])
        y = output.index(analysis["type"].lower())
        x = [0] * input_size

        # Combine permissions and apis to values 0/1 to an array
        async for i in async_generator(data=range(input_size)):
            feature = model_input[i]
            x[i] = 1 if feature in permissions or feature in analysis["apis"] else 0
        Y.append(y)
        X.append(x)

    output_size = 228
    y = np.array(object=Y)
    y = to_categorical(y, output_size)

    matrix_size = 44
    padding_size = matrix_size * matrix_size - input_size
    x = np.array(object=X)
    x = np.concatenate((x, np.zeros((x.shape[0], padding_size))), 1)
    x = x.reshape(x.shape[0], matrix_size, matrix_size, 1)
    return y, x


async def __normalize_permissions(permissions: list):
    return [
        permission.split(".")[-1].upper() 
        async for permission in async_generator(data=permissions)
    ]


def __get_validate_dataset():
    val_path = join(sep, "data","files" ,"files", "dataset", "val.csv")
    val_df = read_csv(filepath_or_buffer=val_path) \
            .sample(frac=1) \
            .drop(['type', 'file_name', 'package'], axis=1, errors="ignore")

    val_y = np.array(val_df.iloc[:, 0])
    val_y = to_categorical(val_y, 228)

    val_x = np.array(val_df.iloc[:, 1:])
    val_x = np.concatenate((val_x, np.zeros((val_x.shape[0], 28))), 1)
    val_x = val_x.reshape(val_x.shape[0], 44, 44, 1)

    return val_y, val_x


def __evaluate(model: Sequential) -> dict:
    test_path = join(sep, "data","files", "files", "dataset", "test.csv")
    test_df = read_csv(filepath_or_buffer=test_path) \
            .sample(frac=1) \
            .drop(['type', 'file_name', 'package'], axis=1, errors="ignore")

    test_y = np.array(test_df.iloc[:, 0])

    test_x = np.array(test_df.iloc[:, 1:])
    test_x = np.concatenate((test_x, np.zeros((test_x.shape[0], 28))), 1)
    test_x = test_x.reshape(test_x.shape[0], 44, 44, 1)

    pred_y = model.predict(x=test_x, verbose=0)
    pred_y = np.argmax(pred_y, axis=1)

    accuracy = accuracy_score(test_y, pred_y)
    precision = precision_score(test_y, pred_y, average="macro", zero_division=0.0)
    recall = recall_score(test_y, pred_y, average="macro")
    f1 = f1_score(test_y, pred_y, average="macro")

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1
    }