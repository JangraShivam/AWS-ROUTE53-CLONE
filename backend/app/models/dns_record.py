from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class DNSRecord(Base):
    __tablename__ = "dns_records"

    id: Mapped[int] = mapped_column(primary_key=True)

    hosted_zone_id: Mapped[int] = mapped_column(
        ForeignKey("hosted_zones.id"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(253),
        nullable=False,
    )

    type: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    value: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    ttl: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=300,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(timezone.utc),
        nullable=False,
    )