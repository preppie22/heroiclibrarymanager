import json
import logging
from pathlib import Path
from typing import List, Union

from heroiclibrarymanager.models.game import HeroicGame

logger = logging.getLogger(__name__)


class HeroicScanner:
    """Scans all games in all Heroic libraries"""

    def __init__(self, config_path: Path, debug: bool = False):
        self.debug = debug
        self.games = []
        self.config_path = config_path

    def scan(self) -> List[HeroicGame]:
        """Scans all supported stores for installed games."""
        if not self.config_path:
            logger.warning("Scanner did not find a config path!")
            return []
        hidden = []
        try:
            with open(self.config_path / "store" / "config.json", "r", encoding="utf-8") as f:
                config_data = json.load(f)
                hidden = config_data.get("games", {}).get("hidden", {})
                logger.debug(f"Loaded hidden games: {hidden}")
        except (json.JSONDecodeError, OSError) as e:
            logger.error(f"Failed to load hidden games from config: {e}")

        store_cache = self.config_path / "store_cache"
        store = self.config_path / "store"
        if not store_cache.exists() or not store.exists():
            return self.games

        # not dealing with zoom or whatever that is for now
        stores = [
            {"title": "GoG", "filename": "gog_library.json"},
            {"title": "Epic Games Store", "filename": "legendary_library.json"},
            {"title": "Amazon Games", "filename": "nile_library.json"}
        ]

        for data in stores:
            file_path = store_cache / data['filename']
            if file_path.exists():
                self.games.extend(self._load_store_games(file_path, hidden, data['title']))
            else:
                logger.debug(f"No library file found for {data['tite']}")

        logger.info(f"Total games found: {len(self.games)}")
        return self.games 

    def _load_store_games(self, file_path: Path, hidden: list, store_title: str) -> List[HeroicGame]:
        """Parses a specific store's database file."""
        games = []        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # get the the first item from the json which is basically the list of games
            items = data[next(iter(data))] # can't hardcode, key for each store is different
            if self.debug:
                dump_path = Path(f"debug_{store_title.lower().replace(' ', '_')}.json")
                with open(dump_path, "w", encoding="utf-8") as dump_file:
                    json.dump(items, dump_file, indent=4)
                logger.debug(f"Dumped {store_title} data to {dump_path}")

            for item in items:
                # sanity check to make sure it's a dict, if not skip it
                if not isinstance(item, dict):
                    continue

                title = item.get("title", "Unknown Title")
                app_name = item.get("app_name", "")
                is_dlc = item.get("install", {}).get("is_dlc", False)
                is_hidden = False
                for hidden_game in hidden:
                    if hidden_game["appName"] == app_name:
                        logger.debug(f"Game {title} ({app_name}) is marked as hidden")
                        is_hidden = True
                        break

                game = HeroicGame(
                    app_name=app_name,
                    title=title,
                    platform=store_title,
                    is_dlc=is_dlc,
                    is_hidden=is_hidden
                )
                games.append(game)

        except (json.JSONDecodeError, OSError) as e:
            logger.error(f"Failed to load games from {file_path}: {e}")

        return games