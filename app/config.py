from pathlib import Path

# Database
BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = f"sqlite:///{BASE_DIR / 'travel_planner.db'}"

# Art Institute of Chicago API
ARTIC_API_BASE_URL = "https://api.artic.edu/api/v1"
