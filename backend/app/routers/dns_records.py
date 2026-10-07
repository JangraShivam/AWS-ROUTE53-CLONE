from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database import get_db
from app.models.dns_record import DNSRecord
from app.models.hosted_zone import HostedZone
from app.models.user import User
from app.schemas.dns_record import (
    DNSRecordCreate,
    DNSRecordResponse,
)
from app.services import dns_record as service


router = APIRouter(
    prefix="/hosted-zones/{zone_id}/records",
    tags=["DNS Records"],
)


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
    # Make sure the hosted zone belongs to the
    # authenticated user.
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

    record = DNSRecord(
        hosted_zone_id=zone.id,
        name=record_data.name,
        type=record_data.type,
        value=record_data.value,
        ttl=record_data.ttl,
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