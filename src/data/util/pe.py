from os.path import join
from functools import reduce
from operator import add
from lief import parse, Binary
import lief.logging
from lief.PE import ALGORITHMS
from src.domain.util import InvalidArgumentException
from src.data.util import get_content, async_generator


# Configure the LIEF logging module
level = lief.logging.LEVEL.ERROR
# set_level(LOGGING_LEVEL.ERROR)
lief.logging.set_level(level)


async def analyze(raw: bytes):
    try:
        binary = parse(raw=raw)
    except:
        raise InvalidArgumentException("Invalid attachment! Only PE format is supported.")

    analysis = {}
    dos_header = __get_dos_header(binary=binary)
    header = __get_header(binary=binary)
    optional_header = __get_optional_header(binary=binary)
    data_directories = __get_data_directories(binary=binary)
    sections = __get_sections(binary=binary)
    _import = __get_import(binary=binary)
    libraries = __get_libraries(binary=binary)
    tls = __get_tls(binary=binary)

    analysis["md5"] = __get_md5(binary=binary)
    analysis["dos_header"] = await dos_header
    analysis["header_characteristics"] = __get_header_characteristics(binary=binary)
    analysis["header"] = await header
    analysis["optional_header"] = await optional_header
    analysis["data_directories"] = await data_directories
    analysis["sections"] = await sections
    analysis["import"] = await _import
    analysis["libraries"] = await libraries
    analysis["tls"] = await tls
    return analysis


def __get_md5(binary: Binary):
    hash = binary.rich_header.hash(ALGORITHMS.MD5)
    md5 = bytes(hash).hex()

    return md5


async def __get_dos_header(binary: Binary):
    fields = await get_content(path=join("libs", "lief", "dos-header.txt"))
    dos_header = {}

    async for field in async_generator(data=fields):
        dos_header[field] = getattr(binary.dos_header, field, None)
    return dos_header


def __get_header_characteristics(binary: Binary):
    characteristics = [characteristic.value for characteristic in binary.header.characteristics_list]
    header_characteristics = reduce(add, characteristics)

    return header_characteristics


async def __get_header(binary: Binary):
    fields = await get_content(path=join("libs", "lief", "header.txt"))
    header = {}

    header["machine"] = binary.header.machine.value
    async for field in async_generator(data=fields):
        value = getattr(binary.header, field, None)
        header[field] = value if field != "signature" else reduce(add, value)
    return header


async def __get_optional_header(binary: Binary):
    fields = await get_content(path=join("libs", "lief", "optional-header.txt"))
    optional_header = {}

    async for field in async_generator(data=fields):
        if field == "magic":
            value = binary.optional_header.magic.value
        elif field == "subsystem":
            value = binary.optional_header.subsystem.value
        else:
            value = getattr(binary.optional_header, field, None)
        optional_header[field] = value
    return optional_header


async def __get_data_directories(binary: Binary):
    fields = await get_content(path=join("libs", "lief", "directory.txt"))
    data_directories = []

    size = len(binary.data_directories)
    size = min(16, size)

    async for i in async_generator(data=range(size)):
        data_directory = {}

        async for field in async_generator(data=fields):
            if field == "section":
                value = await __get_section(directory=binary.data_directories[i])
            elif field == "type":
                value = getattr(binary.data_directories[i], field, None).value
            else:
                value = getattr(binary.data_directories[i], field, None)
            data_directory[field] = value
        data_directories.append(data_directory)
    return data_directories


async def __get_section(directory):
    fields = await get_content(path=join("libs", "lief", "section.txt"))
    directory_value = getattr(directory, "section", None)
    section = {}

    async for field in async_generator(data=fields):
        if field == "name":
            value = getattr(directory.section, field, None)
        elif directory_value is not None:
            value = getattr(directory_value, field, None)
            value = 0 if value is None else value
        else:
            value = 0
        section[field] = value
    return section


async def __get_sections(binary: Binary):
    fields = await get_content(path=join("libs", "lief", "section.txt"))
    sections = []

    size = len(binary.sections)
    size = min(6, size)

    async for i in async_generator(data=range(size)):
        _section = {}

        async for field in async_generator(data=fields):
            try:
                _section[field] = getattr(binary.sections[i], field, None)
            except:
                _section[field] = None if field == "Name" else 0
        sections.append(_section)
    return sections


async def __get_import(binary: Binary):
    if not binary.has_imports:
        return None

    import_directory = binary.imports[0].directory
    fields = await get_content(path=join("libs", "lief", "directory.txt"))
    _import = {}

    async for field in async_generator(data=fields):
        value = getattr(import_directory, field, None)

        if field == "section":
            value = await __get_section(directory=import_directory)
        elif field == "type":
            value = value.value
        _import[field] = value
    return _import


async def __get_libraries(binary: Binary):
    if not binary.has_imports:
        return []

    fields = await get_content(path=join("libs", "lief", "library.txt"))
    
    libraries = []

    size = len(binary.imports)

    async for i in async_generator(data=range(size)):
        library = {}

        # Get library's metadata
        async for field in async_generator(data=fields):
            value = getattr(binary.imports[i], field, None)
            value = 0 if value == None and field != "name" else value
            library[field] = value
        library["entries"] = await __get_library_entries(_import=binary.imports[i])
        libraries.append(library)
        if i == 4:
            break
    return libraries


async def __get_library_entries(_import, limit: int = 5):
    
    fields = await get_content(path=join("libs", "lief", "library-entry.txt"))
    
    library_entries = []

    size = len(_import.entries)
    
    size = min(size, limit)

    async for i in async_generator(data=range(size)):
        library_entry = {}

        async for field in async_generator(data=fields):
            library_entry[field] = getattr(_import.entries[i], field, None)
           
        library_entries.append(library_entry)
    return library_entries


async def __get_tls(binary: Binary):
    if not binary.has_tls:
        return None

    tls = {}

    raw_data_start, raw_data_end = binary.tls.addressof_raw_data
    tls["addressof_callbacks"] = binary.tls.addressof_callbacks
    tls["addressof_index"] = binary.tls.addressof_index
    tls["raw_data_start"] = raw_data_start
    tls["raw_data_end"] = raw_data_end
    tls["characteristics"] = binary.tls.characteristics
    tls["data_directory"] = __get_tsl_data_directory(binary=binary)
    tls["section"] = await __get_tsl_section(binary=binary)
    return tls


def __get_tsl_data_directory(binary: Binary):
    data_directory = {
        "has_section": False,
        "rva": 0,
        "size": 0,
        "type": 0,
        "name": None
    }

    if binary.tls.has_data_directory:
        data_directory["has_section"] = binary.tls.has_data_directory
        data_directory["rva"] = binary.tls.directory.rva
        data_directory["size"] = binary.tls.directory.size
        data_directory["type"] = binary.tls.directory.type.value
        data_directory["name"] = getattr(binary.tls.directory.section, 'name', None)
    return data_directory


async def __get_tsl_section(binary: Binary):
    fields = await get_content(path=join("libs", "lief", "section.txt"))
    section = {}

    fields.remove("name")
    async for field in async_generator(data=fields):
        section[field] = getattr(binary.tls.section, field, 0)
    return section
