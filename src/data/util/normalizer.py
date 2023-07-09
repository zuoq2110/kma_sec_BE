from typing import Optional
from os.path import join
from pandas import read_csv
from src.data.util import async_generator


async def normalize(analysis: dict):
    """
    Normalize PE analysis to an array
    """
    normalized_data_directories = await __normalize_data_directories(analysis["data_directories"])
    normalized_sections = await __normalize_sections(sections=analysis["sections"])
    normalized_import = await __normalize_directory(directory=analysis["import"])
    normalized_libraries = await __normalize_libraries(libraries=analysis["libraries"])
    normalized_tls = await __normalize_tls(tls=analysis["tls"])
    x = []

    x.extend(analysis["dos_header"].values())
    x.append(analysis["header_characteristics"])
    x.extend(analysis["header"].values())
    x.extend(analysis["optional_header"].values())
    x.extend(normalized_data_directories)
    x.extend(normalized_sections)
    x.extend(normalized_import)
    x.extend(normalized_libraries)
    x.extend(normalized_tls)
    return x


async def __normalize_data_directories(data_directories: list):
    x = []

    async for data_directory in async_generator(data=data_directories):
        normalized_directory = __normalize_directory(directory=data_directory)

        x.extend(await normalized_directory)
    return x


async def __normalize_directory(directory: Optional[dict]):
    if directory is None:
        return [0] * 17     # 17 is the number of fields of directory after flattened

    normalized_section = __normalize_section(section=directory["section"])
    x = []

    x.append(1 if directory["has_section"] else 0)
    x.append(directory["rva"])
    x.extend(await normalized_section)
    x.append(directory["size"])
    x.append(directory["type"])
    return x


async def __normalize_section(section: dict):
    x = []

    async for key, value in async_generator(data=section.items()):
        value = value if key != "name" else __encode_section_name(name=value)
        x.append(value)
    return x


def __encode_section_name(name: Optional[str]):
    if name is None:
        return 0

    path = join("libs", "lief", "encoded-sections.csv")
    encoded_sections = read_csv(filepath_or_buffer=path)

    dataframe = encoded_sections.query(f"name == '{name}'")

    if len(dataframe) > 0:
        return dataframe["code"].values[0]

    size = len(encoded_sections)
    code = encoded_sections.tail()["code"].values[0] + 1
    encoded_sections.loc[size] = { "name": name, "code": code }
    encoded_sections.to_csv(path_or_buf=path)
    return code


async def __normalize_sections(sections: list):
    size = len(sections)
    x = []

    async for section in async_generator(data=sections[:5]):
        x.extend(await __normalize_section(section=section))
    # Add padding when the number of sections isn't enought 5
    for _ in range(5 - size):
        x.extend([0] * 13)      # 13 is the number of fields of section
    x.append(1 if size >= 5 else 0)
    return x


async def __normalize_libraries(libraries: list):
    size = len(libraries)
    x = []

    async for library in async_generator(data=libraries):
        async for key, value in async_generator(data=library.items()):
            if key == "entries":
                x.extend(await __normalize_entries(entries=value))
                continue

            if key == "name":
                value = __encode_library_name(name=value)
            x.append(value)

    # Add padding when the number of sections isn't enought 5
    async for _ in async_generator(data=range(5 - size)):
        x.extend([0] * 50)      # 50 is the number of fields of library after flattened
    return x


def __encode_library_name(name: Optional[str]):
    if name is None:
        return 0

    path = join("libs", "lief", "encoded-libraries.csv")
    encoded_libraries = read_csv(filepath_or_buffer=path)

    dataframe = encoded_libraries.query(f"name == '{name}'")

    if len(dataframe) > 0:
        return dataframe["code"].values[0]

    size = len(encoded_libraries)
    code = encoded_libraries.tail()["code"].values[0] + 1
    encoded_libraries.loc[size] = { "name": name, "code": code }
    encoded_libraries.to_csv(path_or_buf=path)
    return code


async def __normalize_entries(entries: list):
    size = len(entries)
    x = []

    async for entry in async_generator(data=entries):
        async for key, value in async_generator(data=entry.items()):
            if key == "is_ordinal":
                value = 1 if value else 0
            elif key == "name":
                value = __encode_entry_name(name=value)
            x.append(value)
    # Add padding when the number of sections isn't enought 5
    async for _ in async_generator(data=range(5 - size)):
        x.extend([0] * 9)      # 9 is the number of fields of library after flattened
    return x


def __encode_entry_name(name: Optional[str]):
    if name is None:
        return 0

    path = join("libs", "lief", "encoded-entries.csv")
    encoded_entries = read_csv(filepath_or_buffer=path)

    dataframe = encoded_entries.query(f"name == '{name}'")

    if len(dataframe) > 0:
        return dataframe["code"].values[0]

    size = len(encoded_entries)
    code = encoded_entries.tail()["code"].values[0] + 1
    encoded_entries.loc[size] = { "name": name, "code": code }
    encoded_entries.to_csv(path_or_buf=path)
    return code


async def __normalize_tls(tls: Optional[dict]):
    if tls is None:
        return [0] * 22      # 22 is the number of fields of TLS after flattened

    fields = ["addressof_callbacks", "addressof_index", "raw_data_start", "raw_data_end", "characteristics"]
    normalized_data_directory = __normalize_tls_data_directory(data_directory=tls["data_directory"])
    normalized_section = [0] * 12 if tls["section"] is None else tls["section"].values()    # 12 is the number of fields of section
    x = []

    x.extend([tls[field] for field in fields])
    x.extend(await normalized_data_directory)
    x.extend(normalized_section)
    return x


async def __normalize_tls_data_directory(data_directory):
    if data_directory is None:
        return [0] * 5   # 12 is the number of fields of data directory

    fields = ["has_section", "rva", "size", "type", "name"]
    x = []

    async for field in async_generator(data=fields):
        value = data_directory[field]

        if field == "has_section":
            value = 1 if value else 0
        elif field == "name":
            value = __encode_section_name(name=value)
        x.append(value)
    return x
