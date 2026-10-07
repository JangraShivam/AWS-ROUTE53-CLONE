from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.hosted_zone import HostedZone
from app.schemas.hosted_zone import HostedZoneCreate


def create(
    db: Session,
    zone_data: HostedZoneCreate,
) -> HostedZone:

    zone = HostedZone(
        domain_name=zone_data.domain_name,
        user_id=zone_data.user_id,
    )

    db.add(zone)
    db.commit()
    db.refresh(zone)

    return zone



def get_by_id(db: Session, zone_id: int) -> HostedZone | None:
    return db.get(HostedZone, zone_id)


def get_all(db: Session) -> list[HostedZone]:
    statement = select(HostedZone)

    result = db.scalars(statement)

    return list(result)


def delete(db: Session, zone: HostedZone) -> None:
    db.delete(zone)
    db.commit()