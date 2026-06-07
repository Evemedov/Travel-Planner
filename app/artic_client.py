import httpx
from app.config import ARTIC_API_BASE_URL


def validate_place_exists(external_id: int) -> dict | None:
    """Fetch a place from the Art Institute of Chicago API.
    Returns the place data dict if found, or None if the place does not exist.
    """
    try:
        response = httpx.get(f"{ARTIC_API_BASE_URL}/places/{external_id}")
        if response.status_code == 200:
            return response.json()["data"]
        return None
    except httpx.HTTPError:
        return None
