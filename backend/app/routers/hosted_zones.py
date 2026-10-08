from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database import get_db
from app.models.dns_record import DNSRecord
from app.models.hosted_zone import HostedZone
from app.models.user import User
from app.schemas.hosted_zone import (
    HostedZoneCreate,
    HostedZoneResponse,
    HostedZoneUpdate,
)


router = APIRouter(
    prefix="/hosted-zones",
    tags=["Hosted Zones"],
)


def serialize_hosted_zone(
    zone: HostedZone,
    db: Session,
) -> dict:
    record_count = (
        db.query(DNSRecord)
        .filter(DNSRecord.hosted_zone_id == zone.id)
        .count()
    )

    return {
        "id": zone.id,
        "domain_name": zone.domain_name,
        "type": zone.type,
        "description": zone.description,
        "record_count": record_count,
        "created_at": zone.created_at,
    }


@router.post(
    "/",
    response_model=HostedZoneResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_hosted_zone(
    zone_data: HostedZoneCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing_zone = (
        db.query(HostedZone)
        .filter(HostedZone.domain_name == zone_data.domain_name)
        .first()
    )

    if existing_zone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hosted zone already exists",
        )

    hosted_zone = HostedZone(
        user_id=current_user.id,
        domain_name=zone_data.domain_name,
        type=zone_data.type,
        description=zone_data.description,
    )

    db.add(hosted_zone)
    db.commit()
    db.refresh(hosted_zone)

    return serialize_hosted_zone(hosted_zone, db)


@router.get(
    "/",
    response_model=list[HostedZoneResponse],
)
def get_hosted_zones(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    zones = (
        db.query(HostedZone)
        .filter(HostedZone.user_id == current_user.id)
        .all()
    )

    return [
        serialize_hosted_zone(zone, db)
        for zone in zones
    ]


@router.get(
    "/{zone_id}",
    response_model=HostedZoneResponse,
)
def get_hosted_zone(
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

    return serialize_hosted_zone(zone, db)


@router.put(
    "/{zone_id}",
    response_model=HostedZoneResponse,
)
def update_hosted_zone(
    zone_id: int,
    zone_data: HostedZoneUpdate,
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

    if zone_data.domain_name is not None and zone_data.domain_name != zone.domain_name:
        existing_zone = (
            db.query(HostedZone)
            .filter(HostedZone.domain_name == zone_data.domain_name)
            .first()
        )

        if existing_zone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hosted zone already exists",
            )

        zone.domain_name = zone_data.domain_name

    if zone_data.type is not None:
        zone.type = zone_data.type

    if "description" in zone_data.model_fields_set:
        zone.description = zone_data.description

    db.commit()
    db.refresh(zone)

    return serialize_hosted_zone(zone, db)


@router.delete(
    "/{zone_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_hosted_zone(
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

    (
        db.query(DNSRecord)
        .filter(DNSRecord.hosted_zone_id == zone.id)
        .delete(synchronize_session=False)
    )
    db.delete(zone)
    db.commit()

    return None
