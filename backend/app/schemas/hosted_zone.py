from datetime import datetime

from pydantic import BaseModel, Field


class HostedZoneCreate(BaseModel):
    domain_name: str = Field(
        min_length=1,
        max_length=255,
    )


class HostedZoneResponse(BaseModel):
    id: int
    domain_name: str
    created_at: datetime

    class Config:
        from_attributes = True