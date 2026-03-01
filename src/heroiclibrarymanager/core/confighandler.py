import time
import shutil
import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

class HeroicConfigHandler:
    def __init__(self, heroic_config_root: Path):
        self.config_root = heroic_config_root
        self.backup_dir = heroic_config_root / "backups_hlm"

    def safe_write_json(self, filename: str, data: dict[str, Any]) -> bool:
        target_file = self.config_root / filename

        if not target_file.exists():
            return False
        
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"{target_file.stem}_{timestamp}{target_file.suffix}"
            shutil.copy2(target_file, backup_path)

            temp_file = target_file.with_suffix(".tmp")
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)

            temp_file.replace(target_file)
            return True
        except Exception:
            logger.exception(f"Failed to safely write to {filename}")
            return False

        return False
