from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.hosted_zone import (
    HostedZoneCreate,
    HostedZoneResponse,
)
from app.services import hosted_zone as service
from app.models.hosted_zone import HostedZone
from app.models.user import User
from app.core.security import get_current_user



router = APIRouter(
    prefix="/hosted-zones",
    tags=["Hosted Zones"],
)


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
    # Check whether this domain already exists
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
    )

    db.add(hosted_zone)
    db.commit()
    db.refresh(hosted_zone)

    return hosted_zone



# ---------------------------------------------------------
# GET ALL HOSTED ZONES
# ---------------------------------------------------------
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

    return zones



# ---------------------------------------------------------
# GET HOSTED ZONE BY ID
# ---------------------------------------------------------
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

    return zone


# ---------------------------------------------------------
# DELETE HOSTED ZONE
# ---------------------------------------------------------
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

    db.delete(zone)
    db.commit()

    return None