"""
config.py

Central app configuration: file paths, server port, Ollama target model.
Everything else in the backend reads from here — no hardcoded paths/ports
scattered across files.

Depends on: nothing (base module).
Called from: main.py, db/connection.py, ollama/client.py, ollama/health.py
"""

from pathlib import Path

# Repo root = two levels up from this file (app/backend/config.py -> repo root)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Where the SQLite database lives. Kept out of git (see .gitignore).
DATA_DIR = BASE_DIR / "app" / "data"
DB_PATH = DATA_DIR / "workstation.db"

# Where skill.md + companion files live (populated in Phase 5).
SKILLS_DIR = BASE_DIR / "app" / "skills"

# Backend server settings. Fixed port for V1 — simpler than dynamic
# port discovery, and this app never needs to coexist with a second
# instance of itself.
HOST = "127.0.0.1"
PORT = 8317

# Ollama connection settings.
OLLAMA_BASE_URL = "http://localhost:11434"

# The model this app expects to use by default. Update once Phase 1
# hardware testing confirms which quant/model fits the target GPU
# (see build plan: GTX 1660 6GB, Q4 target).
DEFAULT_MODEL = "qwen2.5:3b"


def ensure_data_dir() -> None:
    """
    ensure_data_dir
    Creates the data directory on first run if it doesn't exist yet.
    SQLite needs this folder to exist before it can create the .db file.
    @return  None
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
