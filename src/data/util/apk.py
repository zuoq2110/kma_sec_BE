from os import walk
from os.path import exists, join
from uuid import uuid4
from fnmatch import filter
from collections import Counter
from aiofiles.os import makedirs
from asyncio import create_subprocess_shell
from asyncio.subprocess import PIPE
from aioshutil import rmtree
from androguard.core.bytecodes.apk import APK
from .file import save, get_content
from .smali import parse_smali


def get_metadata(apk: APK) -> dict:
    metadata = {}

    metadata["name"] = apk.get_app_name()
    metadata["package"] = apk.get_package()
    metadata["version_code"] = int(apk.get_androidversion_code())
    metadata["version_name"] = apk.get_androidversion_name()
    metadata["user_features"] = apk.get_features()
    metadata["permissions"] = apk.get_permissions()
    metadata["activities"] = apk.get_activities()
    metadata["services"] = apk.get_services()
    metadata["receivers"] = apk.get_receivers()
    return metadata


async def disassamble(apk_bytes: bytes, cache_dir: str) -> list:
    uuid = uuid4().hex
    dir = join(cache_dir, f"{uuid}")
    path = join(dir, f"{uuid}.apk")
    out_dir = join(dir, "out")

    await makedirs(name=dir, exist_ok=True)
    await save(data=apk_bytes, path=path)

    packages = await get_content(path=join('app', 'libs', 'androPyTool', 'packages.txt'))
    classes = await get_content(path=join('app', 'libs', 'androPyTool', 'classes.txt'))
    apis = []

    await decode(apk_path=path, out_dir=out_dir)
    async for smali in get_smali_files(source_dir=out_dir):
        async for package_name, class_name, method_name in parse_smali(smali_path=smali):
            if package_name in packages and class_name in classes and method_name != "<init>":
                api = f"{package_name}.{class_name}.{method_name}"
                apis.append(api)
    apis = [api async for api in each_count(apis=apis)]

    await rmtree(dir)
    return apis


async def decode(apk_path: str, out_dir: str):
    if not exists(out_dir):
        lib_path = join('app', 'libs', 'apktool.jar')
        cmd = f"java -jar {lib_path} d {apk_path} -f --force-manifest --no-assets -o {out_dir} -r"
        proc = await create_subprocess_shell(cmd, stdout=PIPE, stderr=PIPE)

        await proc.communicate()


async def get_smali_files(source_dir: str):
    for root, _, files, in walk(source_dir):
        for file in filter(files, "*.smali"):
            yield join(root, file)


async def each_count(apis: list):
    for key, value in Counter(apis).items():
        yield {"name": key, "frequency": value}
