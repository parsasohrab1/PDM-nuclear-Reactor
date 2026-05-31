"""Backup service for data and models (FR-25)."""

import logging
import shutil
from datetime import datetime
from pathlib import Path

from backend.app.config import Settings

logger = logging.getLogger(__name__)


class BackupService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.backup_root = settings.project_root / settings.backup_path

    def run_backup(self) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = self.backup_root / timestamp
        dest.mkdir(parents=True, exist_ok=True)

        data_dir = self.settings.project_root / "data"
        for sub in ("raw", "models"):
            src = data_dir / sub
            if src.exists():
                shutil.copytree(src, dest / sub, dirs_exist_ok=True)

        logger.info("Backup completed: %s", dest)
        return dest
