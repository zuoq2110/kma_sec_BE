from os.path import join
from hashlib import sha1, sha256
from androguard.core.bytecodes.apk import APK
from androguard.core.analysis.analysis import Analysis
from androguard.core.bytecodes.dvm import DalvikVMFormat
from androguard.decompiler.decompiler import DecompilerDAD
from .file import get_content
from .iterable import async_generator


async def get_metadata(apk: APK) -> dict:
    metadata = {}
    version_code = apk.get_androidversion_code()

    metadata["name"] = apk.get_app_name()
    metadata["package"] = apk.get_package()
    metadata["version_code"] = None if version_code is None else int(version_code)
    metadata["version_name"] = apk.get_androidversion_name()
    metadata["certificates"] = await get_certificates(apk=apk)
    metadata["user_features"] = apk.get_features()
    metadata["permissions"] = apk.get_permissions()
    metadata["activities"] = apk.get_activities()
    metadata["services"] = apk.get_services()
    metadata["receivers"] = apk.get_receivers()
    return metadata


async def get_certificates(apk: APK) -> list:
    certificates = []

    async for cert in async_generator(data=apk.get_certificates()):
        sha_1 = sha1(cert.sha1).hexdigest()
        sha_256 = sha256(cert.sha256).hexdigest()

        certificates.append({"sha1": sha_1, "sha256": sha_256})
    return certificates


async def get_apis(apk: APK) -> list:
    _, dx = await get_analysis(a=apk)
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


async def get_analysis(a: APK) -> tuple[list, Analysis]:
    version = a.get_target_sdk_version()
    d = []
    dx = Analysis()

    async for dex in async_generator(data=a.get_all_dex()):
        df = DalvikVMFormat(dex, using_api=version)

        dx.add(df)
        d.append(df)
        df.set_decompiler(decompiler=DecompilerDAD(d, dx))
    dx.create_xref()
    return d, dx
