from sqlalchemy.orm import Session

from app.models.dns_record import DNSRecord
from app.repositories import dns_record as repository
from app.repositories import hosted_zone as hosted_zone_repository
from app.schemas.dns_record import DNSRecordCreate


def create(
    db: Session,
    zone_id: int,
    record_data: DNSRecordCreate,
) -> DNSRecord:

    zone = hosted_zone_repository.get_by_id(
        db,
        zone_id,
    )

    if zone is None:
        raise ValueError("Hosted zone not found")

    return repository.create(
        db,
        zone_id,
        record_data,
    )


def get_by_zone(
    db: Session,
    zone_id: int,
) -> list[DNSRecord]:

    zone = hosted_zone_repository.get_by_id(
        db,
        zone_id,
    )

    if zone is None:
        raise ValueError("Hosted zone not found")

    return repository.get_by_zone(
        db,
        zone_id,
    )


def get_by_id(
    db: Session,
    zone_id: int,
    record_id: int,
) -> DNSRecord:

    zone = hosted_zone_repository.get_by_id(
        db,
        zone_id,
    )

    if zone is None:
        raise ValueError("Hosted zone not found")

    record = repository.get_by_id(
        db,
        record_id,
    )

    if record is None:
        raise ValueError("DNS record not found")

    if record.hosted_zone_id != zone_id:
        raise ValueError("DNS record does not belong to this hosted zone")

    return record


def delete(
    db: Session,
    zone_id: int,
    record_id: int,
) -> None:

    zone = hosted_zone_repository.get_by_id(
        db,
        zone_id,
    )

    if zone is None:
        raise ValueError("Hosted zone not found")

    record = repository.get_by_id(
        db,
        record_id,
    )

    if record is None:
        raise ValueError("DNS record not found")

    if record.hosted_zone_id != zone_id:
        raise ValueError(
            "DNS record does not belong to this hosted zone"
        )

    repository.delete(db, record)