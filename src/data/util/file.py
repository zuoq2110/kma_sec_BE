from aiofiles import open


async def save(data, path: str):
    async with open(path, mode="wb") as writer:
        await writer.write(data)
        await writer.flush()


async def get_content(path: str):
    async with open(path, mode="r") as reader:
        content = await reader.readlines()
        content = [line.strip() for line in content]
    return content
