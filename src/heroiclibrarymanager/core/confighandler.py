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

    def read_config(self) -> Any:
        config_file = self.config_root / "store" / "config.json"
        config_data = None
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
        except Exception:
            logger.exception(f"Failed to load config file")
        return config_data


    def safe_write_config(self, data: dict[str, Any]) -> bool:
        target_file = self.config_root / "store" / "config.json"

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
            logger.exception(f"Failed to safely write to {target_file}")
            return False
        
    def list_backups(self) -> list:
        if not self.backup_dir.exists():
            return []
        config_files = sorted(self.backup_dir.glob("config_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        backups_list = []
        for file in config_files:
            timestamp = file.stem.split("_", 1)[-1]
            timestamp = time.strptime(timestamp, "%Y%m%d_%H%M%S")
            backups_list.append({
                "name": file.name,
                "path": file,
                "timestamp": timestamp
            })
        return backups_list
    
    def restore_backup(self, backup_path: Path) -> bool:
        target_file = self.config_root / "store" / "config.json"
        if not backup_path.exists() or not target_file.exists():
            logger.warning(f"Backup file {backup_path} or target config {target_file} does not exist!")
            return False
        try:
            shutil.copy2(backup_path, target_file)
            return True
        except Exception:
            logger.exception(f"Failed to restore backup from {backup_path}")
            return False
            
    
if __name__ == "__main__":
    config_path = "/workspaces/heroiclibrarymanager/tests/test_configs"
    config_handler = HeroicConfigHandler(Path(config_path))
    print(config_handler.list_backups())
