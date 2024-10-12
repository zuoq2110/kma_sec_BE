from os import getenv
from typing import Generator
from pymongo import MongoClient
from pymongo.database import Database
import asyncio

username = getenv("DATABASE_USERNAME", "root")
password = getenv("DATABASE_PASSWORD", "")
host = getenv("DATABASE_HOST", "localhost")
port = getenv("DATABASE_PORT", "27017")
name = getenv("DATABASE_NAME", "kma")


async def get_database() -> Generator[Database, None, None]:
    # uri = f'mongodb://{username}:{password}@{host}:{port}/{name}'

    #chỉ chạy test trên windows(mongo atlas)
    # uri =f"mongodb+srv://zuoq2110:PdbbtRMGDnCfZoOG@cluster0.a7gbj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    uri =f"mongodb://root:sWn3lRo9jABGPr5db101F8gq3u8h0Lfm@42.112.213.93:27017/"
    

    client =  MongoClient(uri)
    if client:
        print("Kết nối thành công", client)
    else:
        print("Kết nối thất bại")


    try:
        yield client[name]
        print("client[name]:",client[name])
    finally:
        print("thất bại")

        client.close()
async def main():
    async for db in get_database():
        if db:
            print("Kết nối thành công đến cơ sở dữ liệu!")
            # Thực hiện thêm các kiểm tra hoặc thao tác khác nếu cần
        else:
            print("Không thể kết nối đến cơ sở dữ liệu.")

# Chạy hàm main trong môi trường bất đồng bộ
if __name__ == "__main__":
    asyncio.run(main())