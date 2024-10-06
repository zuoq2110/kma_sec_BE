from src.domain.data.model import WindowsApplication, WindowsApplicationDetails


def as_windows_application(document) -> WindowsApplication:
    return WindowsApplication(
        id=str(object=document['_id']),
        md5=document['md5'],
        malware_type=document['malware_type'],
        created_at=document['created_at'].isoformat(),
        created_by=str(document['created_by']) if 'created_by' in document else None
        
    )


def as_windows_application_details(document) -> WindowsApplicationDetails:
    return WindowsApplicationDetails(
        id=str(object=document['_id']),
        md5=document['md5'],
        dos_header=document['dos_header'],
        header_characteristics=document['header_characteristics'],
        header=document['header'],
        optional_header=document['optional_header'],
        data_directories=document['data_directories'],
        sections=document['sections'],
        _import=document['import'],
        libraries=document['libraries'],
        tls=document['tls'],
        malware_type=document['malware_type'],
        created_at=document['created_at'].isoformat()
    )
