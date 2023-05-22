from pefile import PE
from hashlib import md5
from array import array
from math import log


def extract(pe: PE) -> dict:
    features = {}
    dos_header = get_dos_header(pe=pe)
    file_header = get_file_header(pe=pe)
    optional_header = get_optional_header(pe=pe)
    section_features = extract_sections(pe=pe)
    entry_import_features = extract_entry_import(pe=pe)
    resources_features = extract_resources(pe=pe)
    version_info = get_version_info(pe=pe)
    try:
        file_dll = [entryDLL.dll.decode("utf-8") for entryDLL in pe.DIRECTORY_ENTRY_IMPORT]
    except:
        file_dll = []

    features['MD5'] = md5(string=pe.write()).hexdigest()
    features["SHA-1"] = 1
    features["SHA-256"] = 1
    features["SHA-512"] = 1
    features.update(dos_header)
    features.update(file_header)
    features["Signature"] = pe.NT_HEADERS.Signature
    features.update(optional_header)
    features["LengthOfPeSections"] = len(pe.sections)
    features.update(section_features)
    features.update(entry_import_features)
    try:
        features["ExportNb"] = len(pe.DIRECTORY_ENTRY_EXPORT.symbols)
    except:
        features["ExportNb"] = 0
    features.update(resources_features)
    try:
        features['LoadConfigurationSize'] = pe.DIRECTORY_ENTRY_LOAD_CONFIG.struct.Size
    except:
        features['LoadConfigurationSize'] = 0
    features['VersionInformationSize'] = len([version_info.keys()])
    features['DLL'] = len(file_dll)
    features['LengthOfInformation'] = len(
        features.keys()) + len(features.items())
    return features


def get_dos_header(pe: PE) -> dict:
    dos_header = {}
    pe_dos_header = pe.DOS_HEADER.dump_dict()
    removable_labels = ['Structure', 'e_res', 'e_res2']

    for label in removable_labels:
        pe_dos_header.pop(label)
    for header in pe_dos_header:
        dos_header[header] = pe_dos_header[header]['Value']
    return dos_header


def get_file_header(pe: PE) -> dict:
    file_header = {}
    pe_file_header = pe.FILE_HEADER.dump_dict()
    takable_labels = ['Machine', 'SizeOfOptionalHeader', 'Characteristics']

    for header in pe_file_header:
        if header in takable_labels:
            file_header[header] = pe_file_header[header]['Value']
    return file_header


def get_optional_header(pe: PE) -> dict:
    optional_header = {}
    pe_optional_header = pe.OPTIONAL_HEADER.dump_dict()

    pe_optional_header.pop('Structure')
    for header in pe_optional_header:
        optional_header[header] = pe_optional_header[header]['Value']
    return optional_header


def extract_sections(pe: PE) -> dict:
    features = {}

    entropy = [section.get_entropy() for section in pe.sections]
    features["MeanEntropy"] = sum(entropy) / float(len(entropy))
    features["MinEntropy"] = min(entropy)
    features["MaxEntropy"] = max(entropy)

    raw_sizes = [section.SizeOfRawData for section in pe.sections]
    features["MeanRawSize"] = sum(raw_sizes) / float(len(raw_sizes))
    features["MinRawSize"] = min(entropy)
    features["MaxRawSize"] = max(entropy)

    virtual_sizes = [section.Misc_VirtualSize for section in pe.sections]
    features["MeanVirtualSize"] = sum(
        virtual_sizes) / float(len(virtual_sizes))
    features["MinVirtualSize"] = min(entropy)
    features["MaxVirtualSize"] = max(entropy)
    return features


def extract_entry_import(pe: PE) -> dict:
    try:
        imports = sum([x.imports for x in pe.DIRECTORY_ENTRY_IMPORT], [])
    except:
        imports = 0
    features = {}

    try:
        features["ImportsNbDLL"] = len(pe.DIRECTORY_ENTRY_IMPORT)
    except:
        features["ImportsNbDLL"] = 0
    features["ImportsNb"] = len(imports)
    try:
        features["ImportsNbOrdinal"] = len(len([x for x in imports if x.name is None]))
    except:
        features["ImportsNbOrdinal"] = 0
    return features


def get_entropy(data):
    if len(data) == 0:
        return 0.0

    occurences = array('L', [0] * 256)
    for x in data:
        occurences[x if isinstance(x, int) else ord(x)] += 1

    entropy = 0
    for x in occurences:
        if x:
            p_x = float(x) / len(data)
            entropy -= p_x * log(p_x, 2)

    return entropy


def get_resources(pe: PE) -> list:
    resources = []

    if hasattr(pe, 'DIRECTORY_ENTRY_RESOURCE'):
        for resource_type in pe.DIRECTORY_ENTRY_RESOURCE.entries:
            if not hasattr(resource_type, 'directory'):
                continue

            for resource_id in resource_type.directory.entries:
                if hasattr(resource_id, 'directory'):
                    for resource_lang in resource_id.directory.entries:
                        offset_to_data = resource_lang.data.struct.OffsetToData
                        size = resource_lang.data.struct.Size
                        data = pe.get_data(offset_to_data, size)
                        entropy = get_entropy(data)

                        resources.append([entropy, size])
    return resources


def extract_resources(pe: PE) -> dict:
    resources = get_resources(pe=pe)
    features = {
        'ResourcesMeanEntropy': 0,
        'ResourcesMinEntropy': 0,
        'ResourcesMaxEntropy': 0,
        'ResourcesMeanSize': 0,
        'ResourcesMinSize': 0,
        'ResourcesMaxSize': 0,
    }

    features['ResourcesNb'] = len(resources)
    if len(resources) > 0:
        entropy = [x[0] for x in resources]

        features['ResourcesMeanEntropy'] = sum(entropy) / float(len(entropy))
        features['ResourcesMinEntropy'] = min(entropy)
        features['ResourcesMaxEntropy'] = max(entropy)

        sizes = [x[1] for x in resources]

        features['ResourcesMeanSize'] = sum(sizes) / float(len(sizes))
        features['ResourcesMinSize'] = min(sizes)
        features['ResourcesMaxSize'] = max(sizes)
    return features


def get_version_info(pe: PE) -> dict:
    version = {}
    try:
        pe_file_info = pe.FileInfo
    except:
        pe_file_info = []

    for file_info in pe_file_info:
        for info in file_info:
            if info.Key == 'StringFileInfo':
                for st in info.StringTable:
                    for entry in st.entries.items():
                        version[entry[0]] = entry[1]
            if info.Key == 'VarFileInfo':
                for var in info.Var:
                    version[var.entry.items()[0][0]] = var.entry.items()[0][1]
    if hasattr(pe, 'VS_FIXEDFILEINFO'):
        version['flags'] = pe.VS_FIXEDFILEINFO[0].FileFlags
        version['os'] = pe.VS_FIXEDFILEINFO[0].FileOS
        version['type'] = pe.VS_FIXEDFILEINFO[0].FileType
        version['file_version'] = pe.VS_FIXEDFILEINFO[0].FileVersionLS
        version['product_version'] = pe.VS_FIXEDFILEINFO[0].ProductVersionLS
        version['signature'] = pe.VS_FIXEDFILEINFO[0].Signature
        version['struct_version'] = pe.VS_FIXEDFILEINFO[0].StrucVersion
    return version
