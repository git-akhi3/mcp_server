from pydantic import BaseModel, Field


class GetAllEventsInput(BaseModel):
    page: int = Field(default=0, ge=0)
    size: int = Field(default=10, ge=1, le=50)
    sortBy: str = "eventDateTime"
    sortDir: str = "asc"
    afterDate: str


class GetEventBySlugInput(BaseModel):
    event_slug: str = Field(..., min_length=3)
