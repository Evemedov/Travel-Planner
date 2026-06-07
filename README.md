# Travel Planner API

A FastAPI backend for managing travel projects and places from the [Art Institute of Chicago API](https://api.artic.edu/docs/#places).

## Tech Stack

- **Framework:** FastAPI
- **Database:** SQLite
- **Tests:** pytest

## Running Locally

### Native

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

uvicorn app.main:app --reload
```

### Docker

```bash
docker build -t travel-planner .
docker run -p 8000:8000 travel-planner
```

### Docker Compose

```bash
docker compose up -d
```

The API will be available at `http://localhost:8000`.

Interactive docs (Swagger UI): `http://localhost:8000/docs`
## API Endpoints

### Projects — `/api/v1/projects`

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/projects/` | Create project (optionally with places) |
| GET | `/api/v1/projects/` | List all projects |
| GET | `/api/v1/projects/{id}` | Get project with places |
| PATCH | `/api/v1/projects/{id}` | Update project info |
| DELETE | `/api/v1/projects/{id}` | Delete project |

### Places — `/api/v1/projects/{project_id}/places`

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/projects/{id}/places/` | Add place to project |
| GET | `/api/v1/projects/{id}/places/` | List places in project |
| GET | `/api/v1/projects/{id}/places/{place_id}` | Get single place |
| PATCH | `/api/v1/projects/{id}/places/{place_id}` | Update notes / mark visited |
