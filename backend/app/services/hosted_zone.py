from sqlalchemy.orm import Session

from app.repositories import hosted_zone as repository
from app.schemas.hosted_zone import HostedZoneCreate
from app.models.hosted_zone import HostedZone


def create(
    db: Session,
    user_id: int,
    zone_data: HostedZoneCreate,
) -> HostedZone:
    return repository.create(db, user_id, zone_data)

def get_all(db: Session) -> list[HostedZone]:
    return repository.get_all(db)


def get_by_id(
    db: Session,
    zone_id: int,
) -> HostedZone | None:
    return repository.get_by_id(db, zone_id)


def delete(
    db: Session,
    zone_id: int,
) -> None:
    zone = repository.get_by_id(db, zone_id)

    if zone is None:
        raise ValueError("Hosted zone not found")

    repository.delete(db, zone)
