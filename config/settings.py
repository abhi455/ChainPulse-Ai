from pathlib import Path
import os


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SAMPLE_DATA_DIR = DATA_DIR / "sample"
EXPORT_DATA_DIR = DATA_DIR / "exports"

MODEL_DIR = PROJECT_ROOT / "models"
LOG_DIR = PROJECT_ROOT / "logs"
STORAGE_DIR = PROJECT_ROOT / "storage"

APP_ENV = os.getenv("CHAINPULSE_ENV", "development")
APP_NAME = "ChainPulse AI"
APP_VERSION = "0.1.0"


def ensure_directories() -> None:
    directories = [
        DATA_DIR,
        RAW_DATA_DIR,
        PROCESSED_DATA_DIR,
        SAMPLE_DATA_DIR,
        EXPORT_DATA_DIR,
        MODEL_DIR,
        LOG_DIR,
        STORAGE_DIR,
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


ensure_directories()