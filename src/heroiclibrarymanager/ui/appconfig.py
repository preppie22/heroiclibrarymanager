import logging
from configparser import ConfigParser
from pathlib import Path

logger = logging.getLogger(__name__)

import heroiclibrarymanager.core.environment as app_env

class AppConfig:
    app_config = app_env.Environment().app_config_root
    default_config = {
        "DEFAULT": {
            "library_path": "",
            "window_width": "1400",
            "window_height": "900"
        },
        "Deduplication": {
            "platform_priority": ""
        }
    }

    def __init__(self) -> None:
        self.config = ConfigParser()
        self.config_file = self.app_config / "config.conf"

        if not self.config_file.exists():
            logger.warning(f"Config file {self.config_file} does not exist, creating default config")
            self.config.read_dict(self.default_config)
            try:
                with open(self.config_file, 'w') as f:
                    self.config.write(f)
            except Exception as e:
                logger.exception(f"Failed to create default config file at {self.config_file}: {e}")
        else:
            try:
                self.config.read(self.config_file)
            except Exception as e:
                logger.exception(f"Failed to read config file at {self.config_file}: {e}")

    def get_value(self, section, key):
        return self.config.get(section, key, fallback=None)
    
    def set_value(self, section, key, value):
        if not section == 'DEFAULT' and not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, value)
        try:
            with open(self.config_file, 'w') as f:
                self.config.write(f)
        except Exception as e:
            logger.exception(f"Failed to write config file at {self.config_file}: {e}")
    