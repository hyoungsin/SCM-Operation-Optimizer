from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
OUTPUT_DIR = DATA_DIR / "outputs"
REPORT_DIR = DATA_DIR / "reports"
MONGODB_URI = "mongodb://localhost:27017"
MONGODB_DB_NAME = "scm_milp_poc"
