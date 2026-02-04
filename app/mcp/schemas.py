from pydantic import BaseModel, Field, field_validator
from typing import Literal
import re


class GetAllEventsInput(BaseModel):
    page: int = Field(default=0, ge=0, description="Page number for pagination (0-indexed)")
    size: int = Field(default=4, ge=1, le=50, description="Number of events per page")
    sortBy: str = Field(default="eventDateTime", description="Field to sort by")
    sortDir: Literal["asc", "desc"] = Field(default="asc", description="Sort direction")
    afterDate: str = Field(..., description="ISO 8601 datetime with timezone (e.g., 2026-02-04T00:00:00.000Z)")

    @field_validator('afterDate')
    @classmethod
    def validate_after_date(cls, v: str) -> str:
        pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z$'
        if not re.match(pattern, v):
            raise ValueError('afterDate must be in ISO 8601 format with timezone (e.g., 2026-02-04T00:00:00.000Z)')
        return v

    class Config:
        extra = "forbid"


class GetEventBySlugInput(BaseModel):
    event_slug: str = Field(..., min_length=1, description="Unique slug identifier for the event")

    class Config:
        extra = "forbid"
