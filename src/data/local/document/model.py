from src.domain.data.model import Model, ModelDetails, ModelDataset, ModelHistory


def as_model(document) -> Model:
    return Model(
        id=str(object=document['_id']),
        version=document['version'],
        type=document['type'],
        input_format=document['input_format'],
        created_at=document['created_at'].isoformat()
    )


def as_model_details(document, source_size: int) -> ModelDetails:
    return ModelDetails(
        id=str(object=document['_id']),
        version=document['version'],
        type=document['type'],
        size=source_size,
        input_format=document['input_format'],
        output=document['output'],
        accuracy=document['accuracy'],
        precision=document['precision'],
        recall=document['recall'],
        f1=document['f1'],
        created_at=document['created_at'].isoformat()
    )


def as_model_dataset(document) -> ModelDataset:
    return ModelDataset(
        label=document['label'],
        quantity=document['quantity']
    )


def as_model_history(document) -> ModelHistory:
    return ModelHistory(
        accuracy=document['accuracy'],
        val_accuracy=document['val_accuracy'],
        loss=document['loss'],
        val_loss=document['val_loss'],
    )
