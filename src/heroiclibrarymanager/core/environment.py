from functools import cached_property
import platform
from platformdirs import user_config_path
from pathlib import Path
import os

class Environment:
    """Handles environment-specific paths and configurations for Heroic Library Manager."""
    def __init__(self):
        self.home = Path.home()
        self.os_name = platform.system()

    @cached_property
    def heroic_config_root(self) -> Path | None:
        """ Config folder for heroic """
        if self.os_name == "Linux":
            paths = [
                self.home / ".var/app/com.heroicgameslauncher.hgl/config/heroic",
                self.home / ".config/heroic"
            ]
            for path in paths:
                if path.exists():
                    return path
            return None
        
    @cached_property
    def app_config_root(self) -> Path | None:
        """ Config folder for this app """
        path = user_config_path("heroiclibrarymanager")
        path.mkdir(parents=True, exist_ok=True)
        return path