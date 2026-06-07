from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.artic_client import validate_place_exists
from app.dependencies import get_db
from app.models import Project, ProjectPlace
from app.schemas import PlaceAddToProject, PlaceUpdate, ProjectPlaceResponse

router = APIRouter(
    prefix="/api/v1/projects/{project_id}/places",
    tags=["Project Places"],
)


def _get_project_or_404(project_id: int, db: Session) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found.",
        )
    return project


@router.post("/", response_model=ProjectPlaceResponse, status_code=status.HTTP_201_CREATED)
def add_place_to_project(
    project_id: int, data: PlaceAddToProject, db: Session = Depends(get_db)
):
    project = _get_project_or_404(project_id, db)

    if len(project.places) >= 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A project can have a maximum of 10 places.",
        )

    existing = (
        db.query(ProjectPlace)
        .filter(
            ProjectPlace.project_id == project_id,
            ProjectPlace.external_id == data.external_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Place with external_id {data.external_id} already exists in this project.",
        )

    api_place = validate_place_exists(data.external_id)
    if api_place is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Place with external_id {data.external_id} not found in Art Institute API.",
        )

    place = ProjectPlace(
        project_id=project_id,
        external_id=data.external_id,
        title=api_place["title"],
    )
    db.add(place)
    db.commit()
    db.refresh(place)
    return place


@router.get("/", response_model=list[ProjectPlaceResponse])
def list_places(project_id: int, db: Session = Depends(get_db)):
    _get_project_or_404(project_id, db)
    places = (
        db.query(ProjectPlace)
        .filter(ProjectPlace.project_id == project_id)
        .all()
    )
    return places


@router.get("/{place_id}", response_model=ProjectPlaceResponse)
def get_place(project_id: int, place_id: int, db: Session = Depends(get_db)):
    _get_project_or_404(project_id, db)
    place = (
        db.query(ProjectPlace)
        .filter(
            ProjectPlace.project_id == project_id,
            ProjectPlace.id == place_id,
        )
        .first()
    )
    if place is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Place with id {place_id} not found in project {project_id}.",
        )
    return place


@router.patch("/{place_id}", response_model=ProjectPlaceResponse)
def update_place(
    project_id: int, place_id: int, data: PlaceUpdate, db: Session = Depends(get_db)
):
    _get_project_or_404(project_id, db)
    place = (
        db.query(ProjectPlace)
        .filter(
            ProjectPlace.project_id == project_id,
            ProjectPlace.id == place_id,
        )
        .first()
    )
    if place is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Place with id {place_id} not found in project {project_id}.",
        )

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(place, field, value)

    # Auto-complete project when all places are visited
    if place.is_visited:
        project = _get_project_or_404(project_id, db)
        if all(p.is_visited for p in project.places):
            project.status = "completed"
            project.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(place)
    return place
