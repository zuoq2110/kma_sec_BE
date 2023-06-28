from os.path import join
from androguard.core.bytecodes.apk import APK
from androguard.core.analysis.analysis import Analysis
from .file import get_content
from .iterable import async_generator


def get_metadata(a: APK) -> dict:
    metadata = {}
    version_code = a.get_androidversion_code()

    metadata["name"] = a.get_app_name()
    metadata["package"] = a.get_package()
    metadata["version_code"] = None if version_code is None else int(version_code)
    metadata["version_name"] = a.get_androidversion_name()
    metadata["user_features"] = a.get_features()
    metadata["permissions"] = a.get_permissions()
    metadata["activities"] = a.get_activities()
    metadata["services"] = a.get_services()
    metadata["receivers"] = a.get_receivers()
    return metadata


async def get_apis(dx: Analysis) -> list:
    packages = await get_content(path=join('libs', 'androPyTool', 'packages.txt'))
    classes = await get_content(path=join('libs', 'androPyTool', 'classes.txt'))
    ignore_methods = ["<init>", "<clinit>"]
    apis = set()

    async for class_name, class_analysis in async_generator(data=dx.classes.items()):
        names = class_name[1: -1].split("/")
        package_name = ".".join(names[: -1])

        if package_name not in packages or names[-1] not in classes:
            continue

        async for method in async_generator(data=class_analysis.get_methods()):
            if method.name not in ignore_methods:
                apis.add(f"{package_name}.{names[-1]}.{method.name}")

    return list(apis)
