from unittest.mock import patch
from tests.conftest import MOCK_PLACE_RESPONSE, MOCK_PLACE_RESPONSE_2


class TestCreateProject:
    @patch("app.routers.projects.validate_place_exists")
    def test_create_project_with_places(self, mock_validate, client):
        mock_validate.return_value = MOCK_PLACE_RESPONSE
        response = client.post("/api/v1/projects/", json={
            "name": "Europe Trip",
            "description": "Visiting museums",
            "start_date": "2026-07-01",
            "places": [{"external_id": -2147483613}],
        })
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Europe Trip"
        assert data["status"] == "active"
        assert len(data["places"]) == 1
        assert data["places"][0]["external_id"] == -2147483613
        assert data["places"][0]["title"] == "Peoria"

    def test_create_project_without_places(self, client):
        response = client.post("/api/v1/projects/", json={
            "name": "Empty Project",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Empty Project"
        assert len(data["places"]) == 0

    @patch("app.routers.projects.validate_place_exists")
    def test_create_project_fails_with_more_than_10_places(self, mock_validate, client):
        mock_validate.return_value = MOCK_PLACE_RESPONSE
        places = [{"external_id": i} for i in range(11)]
        response = client.post("/api/v1/projects/", json={
            "name": "Too Many Places",
            "places": places,
        })
        assert response.status_code == 422

    @patch("app.routers.projects.validate_place_exists")
    def test_create_project_fails_with_invalid_place(self, mock_validate, client):
        mock_validate.return_value = None
        response = client.post("/api/v1/projects/", json={
            "name": "Bad Place",
            "places": [{"external_id": 999999}],
        })
        assert response.status_code == 400

    def test_create_project_fails_with_empty_name(self, client):
        response = client.post("/api/v1/projects/", json={
            "name": "",
        })
        assert response.status_code == 422


class TestListProjects:
    def test_list_projects_empty(self, client):
        response = client.get("/api/v1/projects/")
        assert response.status_code == 200
        assert response.json() == []

    @patch("app.routers.projects.validate_place_exists")
    def test_list_projects_returns_projects(self, mock_validate, client):
        mock_validate.return_value = MOCK_PLACE_RESPONSE
        client.post("/api/v1/projects/", json={
            "name": "Trip 1",
            "places": [{"external_id": -2147483613}],
        })
        client.post("/api/v1/projects/", json={"name": "Trip 2"})

        response = client.get("/api/v1/projects/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["places_count"] == 1
        assert data[1]["places_count"] == 0


class TestGetProject:
    def test_get_project(self, client):
        client.post("/api/v1/projects/", json={"name": "My Trip"})
        response = client.get("/api/v1/projects/1")
        assert response.status_code == 200
        assert response.json()["name"] == "My Trip"

    def test_get_project_not_found(self, client):
        response = client.get("/api/v1/projects/999")
        assert response.status_code == 404


class TestUpdateProject:
    def test_update_project(self, client):
        client.post("/api/v1/projects/", json={"name": "Old Name"})
        response = client.patch("/api/v1/projects/1", json={
            "name": "New Name",
            "description": "Updated",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name"
        assert data["description"] == "Updated"

    def test_update_project_not_found(self, client):
        response = client.patch("/api/v1/projects/999", json={"name": "X"})
        assert response.status_code == 404


class TestDeleteProject:
    def test_delete_project(self, client):
        client.post("/api/v1/projects/", json={"name": "To Delete"})
        response = client.delete("/api/v1/projects/1")
        assert response.status_code == 204

        response = client.get("/api/v1/projects/1")
        assert response.status_code == 404

    @patch("app.routers.projects.validate_place_exists")
    def test_delete_project_blocked_when_place_visited(self, mock_validate, client):
        mock_validate.return_value = MOCK_PLACE_RESPONSE
        client.post("/api/v1/projects/", json={
            "name": "Visited Trip",
            "places": [{"external_id": -2147483613}],
        })
        # Mark place as visited
        client.patch("/api/v1/projects/1/places/1", json={"is_visited": True})

        response = client.delete("/api/v1/projects/1")
        assert response.status_code == 400

    def test_delete_project_not_found(self, client):
        response = client.delete("/api/v1/projects/999")
        assert response.status_code == 404
