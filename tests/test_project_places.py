from unittest.mock import patch
from tests.conftest import MOCK_PLACE_RESPONSE, MOCK_PLACE_RESPONSE_2


def _create_project_with_place(client, mock_validate):
    """Helper: create a project with one place and return the response."""
    mock_validate.return_value = MOCK_PLACE_RESPONSE
    return client.post("/api/v1/projects/", json={
        "name": "Test Project",
        "places": [{"external_id": -2147483613}],
    })


class TestAddPlace:
    @patch("app.routers.project_places.validate_place_exists")
    @patch("app.routers.projects.validate_place_exists")
    def test_add_place_to_project(self, mock_create, mock_add, client):
        mock_create.return_value = MOCK_PLACE_RESPONSE
        _create_project_with_place(client, mock_create)

        mock_add.return_value = MOCK_PLACE_RESPONSE_2
        response = client.post("/api/v1/projects/1/places/", json={
            "external_id": 33519,
        })
        assert response.status_code == 201
        assert response.json()["title"] == "Sana'a"

    @patch("app.routers.project_places.validate_place_exists")
    @patch("app.routers.projects.validate_place_exists")
    def test_add_place_fails_invalid_external_id(self, mock_create, mock_add, client):
        mock_create.return_value = MOCK_PLACE_RESPONSE
        _create_project_with_place(client, mock_create)

        mock_add.return_value = None
        response = client.post("/api/v1/projects/1/places/", json={
            "external_id": 999999,
        })
        assert response.status_code == 400

    @patch("app.routers.project_places.validate_place_exists")
    @patch("app.routers.projects.validate_place_exists")
    def test_add_duplicate_place_fails(self, mock_create, mock_add, client):
        mock_create.return_value = MOCK_PLACE_RESPONSE
        _create_project_with_place(client, mock_create)

        mock_add.return_value = MOCK_PLACE_RESPONSE
        response = client.post("/api/v1/projects/1/places/", json={
            "external_id": -2147483613,
        })
        assert response.status_code == 409

    @patch("app.routers.project_places.validate_place_exists")
    @patch("app.routers.projects.validate_place_exists")
    def test_add_place_fails_max_10(self, mock_create, mock_add, client):
        mock_create.return_value = MOCK_PLACE_RESPONSE
        # Create project with 10 places
        places = [{"external_id": i} for i in range(10)]
        client.post("/api/v1/projects/", json={
            "name": "Full Project",
            "places": places,
        })

        mock_add.return_value = {"id": 100, "title": "Extra Place"}
        response = client.post("/api/v1/projects/1/places/", json={
            "external_id": 100,
        })
        assert response.status_code == 400

    def test_add_place_project_not_found(self, client):
        response = client.post("/api/v1/projects/999/places/", json={
            "external_id": 1,
        })
        assert response.status_code == 404


class TestListPlaces:
    @patch("app.routers.projects.validate_place_exists")
    def test_list_places(self, mock_validate, client):
        mock_validate.return_value = MOCK_PLACE_RESPONSE
        _create_project_with_place(client, mock_validate)

        response = client.get("/api/v1/projects/1/places/")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_list_places_project_not_found(self, client):
        response = client.get("/api/v1/projects/999/places/")
        assert response.status_code == 404


class TestGetPlace:
    @patch("app.routers.projects.validate_place_exists")
    def test_get_place(self, mock_validate, client):
        mock_validate.return_value = MOCK_PLACE_RESPONSE
        _create_project_with_place(client, mock_validate)

        response = client.get("/api/v1/projects/1/places/1")
        assert response.status_code == 200
        assert response.json()["external_id"] == -2147483613

    def test_get_place_not_found(self, client):
        client.post("/api/v1/projects/", json={"name": "Empty"})
        response = client.get("/api/v1/projects/1/places/999")
        assert response.status_code == 404


class TestUpdatePlace:
    @patch("app.routers.projects.validate_place_exists")
    def test_update_place_notes(self, mock_validate, client):
        mock_validate.return_value = MOCK_PLACE_RESPONSE
        _create_project_with_place(client, mock_validate)

        response = client.patch("/api/v1/projects/1/places/1", json={
            "notes": "Great museum!",
        })
        assert response.status_code == 200
        assert response.json()["notes"] == "Great museum!"

    @patch("app.routers.projects.validate_place_exists")
    def test_mark_visited_autocompletes_project(self, mock_validate, client):
        mock_validate.return_value = MOCK_PLACE_RESPONSE
        _create_project_with_place(client, mock_validate)

        # Mark the only place as visited
        client.patch("/api/v1/projects/1/places/1", json={"is_visited": True})

        # Project should now be completed
        response = client.get("/api/v1/projects/1")
        assert response.json()["status"] == "completed"

    @patch("app.routers.projects.validate_place_exists")
    def test_mark_visited_does_not_complete_if_others_remain(self, mock_validate, client):
        mock_validate.return_value = MOCK_PLACE_RESPONSE
        # Create project with 2 places
        client.post("/api/v1/projects/", json={
            "name": "Multi Place",
            "places": [
                {"external_id": -2147483613},
                {"external_id": 33519},
            ],
        })

        # Mark only one as visited
        client.patch("/api/v1/projects/1/places/1", json={"is_visited": True})

        # Project should still be active
        response = client.get("/api/v1/projects/1")
        assert response.json()["status"] == "active"

    def test_update_place_not_found(self, client):
        client.post("/api/v1/projects/", json={"name": "Empty"})
        response = client.patch("/api/v1/projects/1/places/999", json={
            "notes": "test",
        })
        assert response.status_code == 404
