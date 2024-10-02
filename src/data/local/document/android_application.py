from src.domain.data.model import AndroidApplication, AndroidApplicationDetails


def as_android_application(document) -> AndroidApplication:
    return AndroidApplication(
        id=str(object=document['_id']),
        name=document['name'],
        package=document['package'],
        version_code=document['version_code'],
        version_name=document['version_name'],
        malware_type=document['malware_type'],
        created_at=document['created_at'].isoformat(),
        created_by=str(document['created_by']) if 'created_by' in document else None
    )


def as_android_application_details(document) -> AndroidApplicationDetails:
    return AndroidApplicationDetails(
        id=str(object=document['_id']),
        name=document['name'],
        package=document['package'],
        version_code=document['version_code'],
        version_name=document['version_name'],
        user_features=document['user_features'],
        permissions=document['permissions'],
        activities=document['activities'],
        services=document['services'],
        receivers=document['receivers'],
        malware_type=document['malware_type'],
        created_at=document['created_at'].isoformat()
    )
