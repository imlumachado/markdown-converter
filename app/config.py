from __future__ import annotations

import os

BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8000").rstrip("/")
GA_ID: str = os.getenv("GA_ID", "")
PORT: int = int(os.getenv("PORT", "8000"))
ADSENSE_ENABLED: bool = os.getenv("ADSENSE_ENABLED", "false").strip().lower() in ("1", "true", "yes", "on")
ADSENSE_CLIENT: str = os.getenv("ADSENSE_CLIENT", "").strip()
ADSENSE_SLOT: str = os.getenv("ADSENSE_SLOT", "").strip()
ADSENSE_SLOT_RESPONSIVE: str = os.getenv("ADSENSE_SLOT_RESPONSIVE", "").strip()
MAX_CONCURRENT_JOBS: int = int(os.getenv("MAX_CONCURRENT_JOBS", "3"))
MAX_JOBS_PER_IP: int = int(os.getenv("MAX_JOBS_PER_IP", "2"))
