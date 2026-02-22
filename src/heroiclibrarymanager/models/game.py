from dataclasses import dataclass, field
from typing import Optional

@dataclass
class HeroicGame:
    app_name: str
    title: str
    platform: str
    is_dlc: bool = False
    is_hidden: bool = False

    @property
    def clean_title(self) -> str:
        return self.title.strip().lower()