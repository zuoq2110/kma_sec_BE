from src.domain.data.model import PdfApplication, PdfApplicationDetails


def as_pdf_application(document) -> PdfApplication:
    return PdfApplication(
        id=str(object=document['_id']),
        name=document['name'],
        malware_type=document['malware_type'],
        created_at=document['created_at'].isoformat(),
        created_by=str(document['created_by']) if 'created_by' in document else None

    )

def as_pdf_application_details(document) -> PdfApplicationDetails:
    return PdfApplicationDetails(
        id=str(object=document['_id']),
        name=document['name'],
        attributes=document['attributes'],
        malware_type=document['malware_type'],
        created_at=document['created_at'].isoformat(),
        created_by=str(document['created_by']) if 'created_by' in document else None

    )


