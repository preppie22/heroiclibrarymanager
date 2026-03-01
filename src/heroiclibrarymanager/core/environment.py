from functools import cached_property
import platform
from platformdirs import user_config_path, user_data_path
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
        if self.os_name != "Linux":
            return None
        
        xdg_base = os.environ.get("XDG_CONFIG_HOME")
        if xdg_base:
            native_path = Path(xdg_base) / "heroic"
        else:
            native_path = self.home / ".config/heroic"

        flatpak_path = self.home / ".var/app/com.heroicgameslauncher.hgl/config/heroic"
        if flatpak_path.exists():
            return flatpak_path
        if native_path.exists():
            return native_path
        return None
        
    @cached_property
    def app_config_root(self) -> Path | None:
        """ Config folder for this app """
        path = user_config_path("heroiclibrarymanager")
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @cached_property
    def app_data_root(self) -> Path | None:
        """ Data folder for this app """
        path = user_data_path("heroiclibrarymanager")
        path.mkdir(parents=True, exist_ok=True)
        return path