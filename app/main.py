from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import create_tables
from app.routers import project_places, projects


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(
    title="Travel Planner API",
    description="Manage travel projects and places from the Art Institute of Chicago API.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(projects.router)
app.include_router(project_places.router)
