"""
Manages duplicate games from multiple stores in Heroic Games Launcher.
"""

import toga
from toga.style import Pack
import logging
from pathlib import Path

from heroiclibrarymanager.core.scanner import HeroicScanner
from heroiclibrarymanager.core.library import GameLibrary
from heroiclibrarymanager.core.confighandler import HeroicConfigHandler
# from heroiclibrarymanager.core.environment import Environment

logger = logging.getLogger(__name__)

class HeroicLibraryManager(toga.App):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config_path = "/workspaces/heroiclibrarymanager/tests/test_configs"
        self.game_library = GameLibrary(HeroicScanner(Path(self.config_path)).scan())
        self.config_handler = HeroicConfigHandler(Path(self.config_path))

    def startup(self):
        icon_path = self.paths.app / "resources" / "icons"
        self.hidden_icon = toga.Icon(icon_path / "hidden.png")
        self.visible_icon = toga.Icon(icon_path / "visible.png")
        # print(icon_path)
        # main_box = toga.Box()

        # added a hint here because the fucking linter shows red squigglies
        self.main_window: toga.MainWindow = toga.MainWindow(
            title=self.formal_name,
            size=(1400, 800)
        )

        self.main_table = toga.Table(
            headings=["Game", "Store"],
            style=Pack(flex=1),
            on_activate=self.toggle_hidden
        )
        self.duplicates_table = toga.Tree(
            headings=["Game", "Store"],
            accessors=["Game", "Store"],
            style=Pack(flex=4)
        )

        # scan_cmd = toga.Command(
        #     self.refresh_library,
        #     text="Reload Libraries",
        #     tooltip="Rescan all store libraries",
        #     icon=toga.Icon(icon_path / "library.png"),
        # )

        scan_dups_cmd = toga.Command(
            self.scan_dups,
            text="Find Duplicates",
            tooltip="Scan all libraries for duplicate games",
            icon=toga.Icon(icon_path / "dup.png")
        )

        save_library_cmd = toga.Command(
            self.save_library,
            text="Save Library",
            tooltip="Save library changes to config",
            icon=toga.Icon(icon_path / "save.png")
        )

        self.main_window.toolbar.add(scan_dups_cmd, save_library_cmd)
        # self.main_window.toolbar.add(scan_dups_cmd)
        split = toga.SplitContainer(style=Pack(flex=1))
        split.content = [
            self.main_table, 
            self.duplicates_table
        ]

        self.main_window.content = split
        self.main_window.show()
        self.refresh_library(self)
        # main_box.add(game_table)


    def toggle_hidden(self, widget, row):
        game_title = getattr(row, "game", None)
        game_store = getattr(row, "store", None)
        game_title = game_title[1].strip() if game_title else None
        game_store = game_store.strip() if game_store else None
        selected_game = self.game_library.find(game_title, game_store)
        self.game_library.toggle_hidden(selected_game)
        if selected_game.is_hidden:
            logger.info(f'{selected_game.title} on {selected_game.platform} is now hidden')
            row.game = (self.hidden_icon, f" {selected_game.title}")
        else:
            logger.info(f'{selected_game.title} on {selected_game.platform} is now visible')
            row.game = (self.visible_icon, f" {selected_game.title}")
        # self.refresh_library(self)
        # self.game_library.toggle_hidden(widget.game)

    def save_library(self, widget):
        config_data = self.config_handler.read_config()
        hidden_game_config = []
        for game in self.game_library:
            if game.is_hidden:
                hidden_game = {}
                hidden_game['appName'] = game.app_name
                hidden_game['title'] = game.title
                hidden_game_config.append(hidden_game)
                logger.info(f"Added {game.title} on {game.platform} to hidden config")
        config_data["games"]["hidden"] = hidden_game_config
        self.config_handler.safe_write_config(config_data)
        logger.info("Library changes saved to config")


    def backups(self, widget):
        """ Work in progress! """
        backups = self.config_handler.list_backups()
        backup_window = toga.Window(title="Config Backups")
        
        logger.info(f"Available backups: {[b['timestamp'] for b in backups]}")
        import time
        backup_table = toga.Table(
            headings=["Timestamp"]
        )
        for backup in backups:
            backup_table.data.append((
                time.strftime("%Y-%m-%d %H:%M:%S", backup["timestamp"])
            ))
        restore_button = toga.Button(
            "Restore Selected Backup",
            flex=1,
            on_press=lambda w: {

            }
        )
        backup_button = toga.Button(
            "Create New Backup",
            flex=1,
            on_press=lambda w: print("Backup functionality not implemented yet")
        )
        close_button = toga.Button(
            "Close",
            flex=1,
            on_press=lambda w: backup_window.close()
        )
        button_box = toga.Box(
            children=[restore_button, backup_button, close_button],
            style=Pack(direction="column", margin=10, gap=10)
        )
        split = toga.SplitContainer(style=Pack(flex=1))
        split.content = [backup_table, button_box]
        backup_window.content = split
        backup_window.show()
        

    def refresh_library(self, widget):
        self.main_table.data.clear()
        sorted_games = sorted(
            self.game_library, 
            key=lambda g: (g.title.lower(), g.platform.lower())
        )
        for game in sorted_games:
            if game.is_dlc: continue
            if game.is_hidden:
                # self.main_table.data.append({
                #     "icon": self.hidden_icon,
                #     "title": f" {game.title}",
                #     "subtitle": f"Hidden on {game.platform}"
                # })
                self.main_table.data.append((
                    (self.hidden_icon, f" {game.title}"),
                    game.platform
                ))
            else:
                # self.main_table.data.append({
                #     "icon": self.visible_icon,
                #     "title": game.title,
                #     "subtitle": game.platform
                # })
                self.main_table.data.append((
                    (self.visible_icon, f" {game.title}"),
                    game.platform
                ))

    def scan_dups(self, widget):
        self.duplicates_table.data.clear()
        tree_data = []
        for game_dups in self.game_library.get_duplicates():
            if not game_dups: continue

            first_game = game_dups[0]
            parent_node = {
                "Game": f"{first_game.title} ({len(game_dups)} copies)",
                "Store": ""
            }
            children = []
            for game in game_dups:
                child_data = {
                    "Game": (self.visible_icon, f" {game.title}"),
                    "Store": game.platform
                }
                children.append((child_data, None))
            tree_data.append((parent_node, children))
        sorted_data = sorted(tree_data, key=lambda t: t[0]["Game"])
        self.duplicates_table.data = sorted_data
            
def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    return HeroicLibraryManager(
        "Heroic Library Manager",
        "io.github.preppie22.heroiclibrarymanager",
    )
