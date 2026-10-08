from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database import get_db
from app.models.dns_record import DNSRecord
from app.models.hosted_zone import HostedZone
from app.models.user import User
from app.schemas.dns_record import (
    DNSRecordCreate,
    DNSRecordType,
    DNSRecordResponse,
    DNSRecordUpdate,
)


router = APIRouter(
    prefix="/hosted-zones/{zone_id}/records",
    tags=["DNS Records"],
)


def get_user_zone(
    zone_id: int,
    current_user: User,
    db: Session,
) -> HostedZone:
    zone = (
        db.query(HostedZone)
        .filter(
            HostedZone.id == zone_id,
            HostedZone.user_id == current_user.id,
        )
        .first()
    )

    if zone is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hosted zone not found",
        )

    return zone


def ensure_record_name_available(
    db: Session,
    zone_id: int,
    record_name: str,
    record_type: DNSRecordType | str,
    record_id: int | None = None,
) -> None:
    record_type_value = (
        record_type.value
        if isinstance(record_type, DNSRecordType)
        else record_type
    )

    query = (
        db.query(DNSRecord)
        .filter(
            DNSRecord.hosted_zone_id == zone_id,
            DNSRecord.name == record_name,
        )
    )

    if record_id is not None:
        query = query.filter(DNSRecord.id != record_id)

    records_with_name = query.all()

    if any(record.type == record_type_value for record in records_with_name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A record with this name and type already exists",
        )

    if record_type_value == DNSRecordType.CNAME.value and records_with_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CNAME records cannot share a name with other records",
        )

    if any(record.type == DNSRecordType.CNAME.value for record in records_with_name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Records cannot share a name with an existing CNAME record",
        )


def to_validation_error_detail(error: ValidationError):
    return [
        {
            "loc": item["loc"],
            "msg": item["msg"],
            "type": item["type"],
        }
        for item in error.errors()
    ]


@router.post(
    "/",
    response_model=DNSRecordResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_dns_record(
    zone_id: int,
    record_data: DNSRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    zone = get_user_zone(zone_id, current_user, db)
    ensure_record_name_available(
        db,
        zone.id,
        record_data.name,
        record_data.type,
    )

    record = DNSRecord(
        hosted_zone_id=zone.id,
        name=record_data.name,
        type=record_data.type.value,
        value=record_data.value,
        ttl=record_data.ttl,
        routing_policy=record_data.routing_policy,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record


@router.get(
    "/",
    response_model=list[DNSRecordResponse],
)
def get_dns_records(
    zone_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    zone = get_user_zone(zone_id, current_user, db)

    records = (
        db.query(DNSRecord)
        .filter(DNSRecord.hosted_zone_id == zone.id)
        .all()
    )

    return records


@router.get(
    "/{record_id}",
    response_model=DNSRecordResponse,
)
def get_dns_record(
    zone_id: int,
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    zone = get_user_zone(zone_id, current_user, db)

    record = (
        db.query(DNSRecord)
        .filter(
            DNSRecord.id == record_id,
            DNSRecord.hosted_zone_id == zone.id,
        )
        .first()
    )

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="DNS record not found",
        )

    return record



@router.put(
    "/{record_id}",
    response_model=DNSRecordResponse,
)
def update_dns_record(
    zone_id: int,
    record_id: int,
    record_data: DNSRecordUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    zone = get_user_zone(zone_id, current_user, db)

    record = (
        db.query(DNSRecord)
        .filter(
            DNSRecord.id == record_id,
            DNSRecord.hosted_zone_id == zone.id,
        )
        .first()
    )

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="DNS record not found",
        )

    updates = record_data.model_dump(exclude_unset=True)

    try:
        validated = DNSRecordCreate(
            name=updates.get("name", record.name),
            type=updates.get("type", record.type),
            value=updates.get("value", record.value),
            ttl=updates.get("ttl", record.ttl),
            routing_policy=updates.get("routing_policy", record.routing_policy),
        )
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=to_validation_error_detail(exc),
        ) from exc

    ensure_record_name_available(
        db,
        zone.id,
        validated.name,
        validated.type,
        record_id=record.id,
    )

    record.name = validated.name
    record.type = validated.type.value
    record.value = validated.value
    record.ttl = validated.ttl
    record.routing_policy = validated.routing_policy

    db.commit()
    db.refresh(record)

    return record


@router.delete(
    "/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_dns_record(
    zone_id: int,
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    zone = get_user_zone(zone_id, current_user, db)

    record = (
        db.query(DNSRecord)
        .filter(
            DNSRecord.id == record_id,
            DNSRecord.hosted_zone_id == zone.id,
        )
        .first()
    )

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="DNS record not found",
        )

    db.delete(record)
    db.commit()

    return None
