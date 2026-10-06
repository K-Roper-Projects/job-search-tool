from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class EmploymentType(StrEnum):
    PERMANENT = "permanent"
    CONTRACT = "contract"
    TEMPORARY = "temporary"
    FIXED_TERM = "fixed_term"
    INTERNSHIP = "internship"
    OTHER = "other"
    UNKNOWN = "unknown"


class WorkplaceType(StrEnum):
    ONSITE = "onsite"
    HYBRID = "hybrid"
    REMOTE = "remote"
    UNKNOWN = "unknown"


@dataclass(slots=True)
class Job:
    source: str
    title: str
    source_job_id: str | None = None
    company: str | None = None
    description: str | None = None
    location: str | None = None
    employment_type: EmploymentType = EmploymentType.UNKNOWN
    workplace_type: WorkplaceType = WorkplaceType.UNKNOWN
    salary_min: float | None = None
    salary_max: float | None = None
    salary_currency: str | None = None
    salary_period: str | None = None
    posted_at: datetime | None = None
    expires_at: datetime | None = None
    job_url: str | None = None
    apply_url: str | None = None
    department: str | None = None
    category: str | None = None
    retrieved_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    source_fields: dict[str, Any] = field(default_factory=dict)
