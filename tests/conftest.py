import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import Base
from app.dependencies import get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client():
    return TestClient(app)


MOCK_PLACE_RESPONSE = {
    "id": -2147483613,
    "title": "Peoria",
    "api_model": "places",
    "api_link": "https://api.artic.edu/api/v1/places/-2147483613",
    "tgn_id": None,
}

MOCK_PLACE_RESPONSE_2 = {
    "id": 33519,
    "title": "Sana'a",
    "api_model": "places",
    "api_link": "https://api.artic.edu/api/v1/places/33519",
    "tgn_id": None,
}
