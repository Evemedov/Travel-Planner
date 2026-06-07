from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.artic_client import validate_place_exists
from app.dependencies import get_db
from app.models import Project, ProjectPlace
from app.schemas import ProjectCreate, ProjectListResponse, ProjectResponse, ProjectUpdate

router = APIRouter(prefix="/api/v1/projects", tags=["Projects"])


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(data: ProjectCreate, db: Session = Depends(get_db)):
    project = Project(
        name=data.name,
        description=data.description,
        start_date=str(data.start_date) if data.start_date else None,
    )

    if data.places:
        if len(data.places) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A project can have a maximum of 10 places.",
            )

        seen_ids = set()
        for place_data in data.places:
            if place_data.external_id in seen_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Duplicate external_id {place_data.external_id} in request.",
                )
            seen_ids.add(place_data.external_id)

            api_place = validate_place_exists(place_data.external_id)
            if api_place is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Place with external_id {place_data.external_id} not found in Art Institute API.",
                )

            project.places.append(
                ProjectPlace(
                    external_id=place_data.external_id,
                    title=api_place["title"],
                )
            )

    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/", response_model=list[ProjectListResponse])
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    result = []
    for project in projects:
        result.append(
            ProjectListResponse(
                id=project.id,
                name=project.name,
                description=project.description,
                start_date=project.start_date,
                status=project.status,
                places_count=len(project.places),
                created_at=project.created_at,
                updated_at=project.updated_at,
            )
        )
    return result


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found.",
        )
    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, data: ProjectUpdate, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found.",
        )

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "start_date" and value is not None:
            value = str(value)
        setattr(project, field, value)

    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found.",
        )

    has_visited = any(place.is_visited for place in project.places)
    if has_visited:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete a project that has visited places.",
        )

    db.delete(project)
    db.commit()
