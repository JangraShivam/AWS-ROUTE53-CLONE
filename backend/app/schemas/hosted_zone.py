from datetime import datetime
import re

from pydantic import BaseModel, Field, field_validator
from typing import Literal


DOMAIN_PATTERN = re.compile(
    r"^(?=.{1,253}$)(?!-)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$"
)


def normalize_domain_name(value: str) -> str:
    domain = value.strip().lower().rstrip(".")

    if not DOMAIN_PATTERN.fullmatch(domain):
        raise ValueError("Enter a valid domain name, such as example.com")

    return domain


class HostedZoneCreate(BaseModel):
    domain_name: str = Field(
        min_length=1,
        max_length=255,
    )
    type: Literal["Public", "Private"] = "Public"
    description: str | None = Field(
        default=None,
        max_length=256,
    )

    @field_validator("domain_name")
    @classmethod
    def validate_domain_name(cls, value: str) -> str:
        return normalize_domain_name(value)

    @field_validator("description")
    @classmethod
    def clean_description(cls, value: str | None) -> str | None:
        if value is None:
            return None

        description = value.strip()
        return description or None


class HostedZoneUpdate(BaseModel):
    domain_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    type: Literal["Public", "Private"] | None = None
    description: str | None = Field(
        default=None,
        max_length=256,
    )

    @field_validator("domain_name")
    @classmethod
    def validate_domain_name(cls, value: str | None) -> str | None:
        if value is None:
            return None

        return normalize_domain_name(value)

    @field_validator("description")
    @classmethod
    def clean_description(cls, value: str | None) -> str | None:
        if value is None:
            return None

        description = value.strip()
        return description or None


class HostedZoneResponse(BaseModel):
    id: int
    domain_name: str
    type: str
    description: str | None = None
    record_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True
