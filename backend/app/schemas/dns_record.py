from datetime import datetime
from enum import Enum
import ipaddress
import re

from pydantic import BaseModel, Field, field_validator, model_validator


DNS_NAME_PATTERN = re.compile(
    r"^(?=.{1,253}$)[a-z0-9_*](?:[a-z0-9_*.-]{0,251}[a-z0-9_*])?$"
)
DOMAIN_VALUE_PATTERN = re.compile(
    r"^(?=.{1,253}\.?$)(?!-)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}\.?$"
)
ROUTING_POLICIES = {
    "Simple routing",
    "Weighted",
    "Latency",
    "Failover",
    "Geolocation",
}

class DNSRecordType(str, Enum):
    A = "A"
    AAAA = "AAAA"
    CNAME = "CNAME"
    CAA = "CAA"
    MX = "MX"
    TXT = "TXT"
    NS = "NS"
    DS = "DS"
    NAPTR = "NAPTR"
    PTR = "PTR"
    SRV = "SRV"
    SOA = "SOA"


def split_values(value: str) -> list[str]:
    return [
        part.strip()
        for part in value.splitlines()
        if part.strip()
    ]


def normalize_record_name(value: str) -> str:
    name = value.strip().lower().rstrip(".")

    if name == "@":
        return ""

    if not name:
        return ""

    if not DNS_NAME_PATTERN.fullmatch(name):
        raise ValueError("Enter a valid record name")

    if ".." in name:
        raise ValueError("Record name cannot contain empty labels")

    for label in name.split("."):
        if len(label) > 63:
            raise ValueError("Each record name label must be 63 characters or fewer")

    return name


def normalize_routing_policy(value: str) -> str:
    policy = value.strip()

    if policy not in ROUTING_POLICIES:
        raise ValueError("Select a supported routing policy")

    return policy


def validate_domain_value(value: str, label: str) -> None:
    if not DOMAIN_VALUE_PATTERN.fullmatch(value.strip().lower()):
        raise ValueError(f"{label} must be a valid domain name")


def validate_record_value(
    record_type: DNSRecordType,
    value: str,
) -> str:
    cleaned = value.strip()
    values = split_values(cleaned)

    if not values:
        raise ValueError("Record value is required")

    if record_type == DNSRecordType.A:
        for item in values:
            try:
                ipaddress.IPv4Address(item)
            except ValueError as exc:
                raise ValueError("A records must contain valid IPv4 addresses") from exc

    elif record_type == DNSRecordType.AAAA:
        for item in values:
            try:
                ipaddress.IPv6Address(item)
            except ValueError as exc:
                raise ValueError("AAAA records must contain valid IPv6 addresses") from exc

    elif record_type == DNSRecordType.CNAME:
        if len(values) != 1:
            raise ValueError("CNAME records can contain exactly one target")
        validate_domain_value(values[0], "CNAME target")

    elif record_type == DNSRecordType.NS:
        for item in values:
            validate_domain_value(item, "NS value")

    elif record_type == DNSRecordType.MX:
        for item in values:
            parts = item.split()
            if len(parts) != 2 or not parts[0].isdigit():
                raise ValueError("MX records must use 'priority host' format")

            priority = int(parts[0])
            if priority < 0 or priority > 65535:
                raise ValueError("MX priority must be between 0 and 65535")

            validate_domain_value(parts[1], "MX host")

    elif record_type == DNSRecordType.SRV:
        for item in values:
            parts = item.split()
            if len(parts) != 4 or not all(part.isdigit() for part in parts[:3]):
                raise ValueError(
                    "SRV records must use 'priority weight port target' format"
                )

            port = int(parts[2])
            if port < 0 or port > 65535:
                raise ValueError("SRV port must be between 0 and 65535")

            validate_domain_value(parts[3], "SRV target")

    elif record_type == DNSRecordType.CAA:
        for item in values:
            parts = item.split(maxsplit=2)
            if len(parts) != 3 or not parts[0].isdigit():
                raise ValueError("CAA records must use 'flags tag value' format")

            flags = int(parts[0])
            if flags < 0 or flags > 255:
                raise ValueError("CAA flags must be between 0 and 255")

            if parts[1] not in {"issue", "issuewild", "iodef"}:
                raise ValueError("CAA tag must be issue, issuewild, or iodef")

    elif record_type == DNSRecordType.PTR:
        for item in values:
            validate_domain_value(item, "PTR value")

    elif record_type == DNSRecordType.DS:
        for item in values:
            parts = item.split()
            if len(parts) != 4 or not all(part.isdigit() for part in parts[:3]):
                raise ValueError(
                    "DS records must use 'key_tag algorithm digest_type digest' format"
                )

            if not re.fullmatch(r"[a-fA-F0-9]+", parts[3]):
                raise ValueError("DS digest must be hexadecimal")

    elif record_type == DNSRecordType.SOA:
        for item in values:
            parts = item.split()
            if len(parts) != 7:
                raise ValueError(
                    "SOA records must use 'mname rname serial refresh retry expire minimum' format"
                )

            validate_domain_value(parts[0], "SOA primary nameserver")
            validate_domain_value(parts[1], "SOA responsible mailbox")

            if not all(part.isdigit() for part in parts[2:]):
                raise ValueError("SOA timing fields must be numbers")

    elif record_type == DNSRecordType.NAPTR:
        for item in values:
            parts = item.split(maxsplit=5)
            if len(parts) != 6 or not parts[0].isdigit() or not parts[1].isdigit():
                raise ValueError(
                    "NAPTR records must use 'order preference flags service regexp replacement' format"
                )

    return "\n".join(values)




class DNSRecordCreate(BaseModel):
    name: str = Field(
        min_length=0,
        max_length=253,
    )

    type: DNSRecordType

    value: str = Field(
        min_length=1,
    )

    ttl: int = Field(
        default=300,
        ge=0,
        le=2147483647,
    )

    routing_policy: str = Field(
        default="Simple routing",
        min_length=1,
        max_length=50,
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        return normalize_record_name(value)

    @field_validator("routing_policy")
    @classmethod
    def validate_routing_policy(cls, value: str) -> str:
        return normalize_routing_policy(value)

    @model_validator(mode="after")
    def validate_dns_value(self):
        self.value = validate_record_value(
            self.type,
            self.value,
        )
        return self


class DNSRecordUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=0,
        max_length=253,
    )

    type: DNSRecordType | None = None

    value: str | None = Field(
        default=None,
        min_length=1,
    )

    ttl: int | None = Field(
        default=None,
        ge=0,
        le=2147483647,
    )

    routing_policy: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return None

        return normalize_record_name(value)

    @field_validator("routing_policy")
    @classmethod
    def validate_routing_policy(cls, value: str | None) -> str | None:
        if value is None:
            return None

        return normalize_routing_policy(value)


class DNSRecordResponse(BaseModel):
    id: int
    hosted_zone_id: int
    name: str
    type: str
    value: str
    ttl: int
    routing_policy: str
    created_at: datetime

    class Config:
        from_attributes = True
