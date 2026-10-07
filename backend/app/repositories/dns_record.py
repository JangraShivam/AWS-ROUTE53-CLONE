from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.dns_record import DNSRecord
from app.schemas.dns_record import DNSRecordCreate


def create(
    db: Session,
    zone_id: int,
    record_data: DNSRecordCreate,
) -> DNSRecord:

    record = DNSRecord(
        hosted_zone_id=zone_id,
        name=record_data.name,
        type=record_data.type,
        value=record_data.value,
        ttl=record_data.ttl,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record


def get_by_id(db: Session, record_id: int) -> DNSRecord | None:
    return db.get(DNSRecord, record_id)


def get_by_zone(db: Session, zone_id: int) -> list[DNSRecord]:

    statement = select(DNSRecord).where(
        DNSRecord.hosted_zone_id == zone_id
    )

    result = db.scalars(statement)

    return list(result)


def get_all(db: Session) -> list[DNSRecord]:
    statement = select(DNSRecord)
    result = db.scalars(statement)

    return list(result)


def delete(db: Session, record: DNSRecord) -> None:
    db.delete(record)
    db.commit()


