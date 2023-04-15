from re import sub, split
from .file import get_content
from .iterable import async_generator


async def parse_smali(smali_path: str):
    content = await get_content(path=smali_path)
    lines = [line async for line in async_generator(data=content) if 'invoke-' in line or 'invoke-virtual' in line or 'invoke-direct' in line]

    async for line in async_generator(data=lines):
        api = sub("\{[^]]*\}", lambda x: x.group(0).replace(',', ''), line)
        elements = split(', |;->', api)

        if len(elements) != 2:
            try:
                package = elements[1]
                method = elements[2]
            except:
                pass
        else:
            package = "Object"
            method = elements[1]

        method_name = method.split('(')[0]

        if package.startswith("L"):
            package = package[1:]

        package_names = package.split("/")
        package_name = ".".join(package_names[:-1])
        class_name = package_names[-1]

        yield package_name, class_name, method_name
