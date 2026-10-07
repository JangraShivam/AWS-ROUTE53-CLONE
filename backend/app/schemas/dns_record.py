from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from enum import Enum


# check it

class DNSRecordType(str, Enum):
    A = "A"
    AAAA = "AAAA"
    CNAME = "CNAME"
    MX = "MX"
    TXT = "TXT"
    NS = "NS"
    PTR = "PTR"
    SOA = "SOA"




class DNSRecordCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=253,
    )

    type: str = Field(
        min_length=1,
        max_length=10,
    )

    value: str = Field(
        min_length=1,
    )

    ttl: int = Field(
        default=300,
        ge=0,
    )


class DNSRecordResponse(BaseModel):
    id: int
    hosted_zone_id: int
    name: str
    type: str
    value: str
    ttl: int
    created_at: datetime

    class Config:
        from_attributes = True