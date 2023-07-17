from src.domain.data.model import WindowsApplication


def as_windows_application(document) -> WindowsApplication:
    return WindowsApplication(
        id=str(object=document['_id']),
        md5=document['md5'],
        malware_type=document['malware_type'],
        created_at=document['created_at'].isoformat()
    )
