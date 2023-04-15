from os import getenv
from typing import Generator
from pymongo import MongoClient
from pymongo.database import Database

username = getenv("DATABASE_USERNAME", "root")
password = getenv("DATABASE_PASSWORD", "")
host = getenv("DATABASE_HOST", "localhost")
port = getenv("DATABASE_PORT", "27017")
name = getenv("DATABASE_NAME", "ksecurity")


async def get_database() -> Generator[Database, None, None]:
    uri = f'mongodb://{username}:{password}@{host}:{port}/{name}'
    client = MongoClient(uri)

    try:
        yield client[name]
    finally:
        client.close()
