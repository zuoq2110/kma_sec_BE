from src.domain.data.model import User


def as_user(document) -> User:
    return User(
        id=str(object=document['_id']),
        username=str(object=document['username']),
        password=str(object=document['password'])
    )