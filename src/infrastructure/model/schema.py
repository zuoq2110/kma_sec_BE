from pydantic import BaseModel


class ModelStateBody(BaseModel):
    state: str
