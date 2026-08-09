from __future__ import annotations

import os

BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8000").rstrip("/")
GA_ID: str = os.getenv("GA_ID", "")
PORT: int = int(os.getenv("PORT", "8000"))
