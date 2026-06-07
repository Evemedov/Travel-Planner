from datetime import date, datetime
from pydantic import BaseModel, Field


# --- Place Schemas ---


class ProjectPlaceCreate(BaseModel):
    """Used inside ProjectCreate to attach places at project creation."""

    external_id: int


class PlaceAddToProject(BaseModel):
    """Used when adding a single place to an existing project."""

    external_id: int


class PlaceUpdate(BaseModel):
    """Partial update for a place: notes and/or visited status."""

    notes: str | None = None
    is_visited: bool | None = None


class ProjectPlaceResponse(BaseModel):
    """Place data returned in API responses."""

    id: int
    external_id: int
    title: str
    notes: str | None
    is_visited: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Project Schemas ---


class ProjectCreate(BaseModel):
    """Request body for creating a new project."""

    name: str = Field(..., min_length=1)
    description: str | None = None
    start_date: date | None = None
    places: list[ProjectPlaceCreate] | None = Field(default=None, max_length=10)


class ProjectUpdate(BaseModel):
    """Partial update for project info."""

    name: str | None = Field(default=None, min_length=1)
    description: str | None = None
    start_date: date | None = None


class ProjectResponse(BaseModel):
    """Full project with nested places — used for single project detail."""

    id: int
    name: str
    description: str | None
    start_date: date | None
    status: str
    places: list[ProjectPlaceResponse]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectListResponse(BaseModel):
    """Lightweight project — used in list endpoint (no nested places, just count)."""

    id: int
    name: str
    description: str | None
    start_date: date | None
    status: str
    places_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
