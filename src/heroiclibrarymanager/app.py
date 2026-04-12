"""
Manages duplicate games from multiple stores in Heroic Games Launcher.
"""

import toga
from toga.style import Pack
from toga.sources import TreeSource
from toga.constants import Direction

import logging
from pathlib import Path

from heroiclibrarymanager.core.scanner import HeroicScanner
from heroiclibrarymanager.core.library import GameLibrary
from heroiclibrarymanager.core.confighandler import HeroicConfigHandler
from heroiclibrarymanager.core.hider import HeroicDupsHider

from heroiclibrarymanager.ui.appconfig import AppConfig
from heroiclibrarymanager.ui.dedupconfig import DedupConfig

# from heroiclibrarymanager.core.environment import Environment

logger = logging.getLogger(__name__)

class HeroicLibraryManager(toga.App):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config_path = "/workspaces/heroiclibrarymanager/tests/test_configs"
        self.game_library = GameLibrary(HeroicScanner(Path(self.config_path)).scan())
        self.config_handler = HeroicConfigHandler(Path(self.config_path))
        self.app_config = AppConfig()
        self.duplicates = []

    def startup(self):
        icon_path = self.paths.app / "resources" / "icons"
        self.hidden_icon = toga.Icon(icon_path / "hidden.png")
        self.visible_icon = toga.Icon(icon_path / "visible.png")
        
        window_width = self.app_config.get_value('DEFAULT', 'window_width')
        if not window_width:
            window_width = 1400
            self.app_config.set_value('DEFAULT', 'window_width', str(window_width))
        else:
            window_width = int(window_width)

        window_height = self.app_config.get_value('DEFAULT', 'window_height')
        if not window_height:
            window_height = 900
            self.app_config.set_value('DEFAULT', 'window_height', str(window_height))
        else:
            window_height = int(window_height)

        # added a hint here because the fucking linter shows red squigglies
        self.main_window: toga.MainWindow = toga.MainWindow(
            title=self.formal_name,
            size=(window_width, window_height),
        )

        # LEFT SIDE OF MAIN WINDOW
        self.left_side = toga.Box(
            style=Pack(direction='column')
        )
        self.main_table = toga.Table(
            headings=["Game", "Store"],
            on_activate=self.toggle_hidden,
            style=Pack(flex=1)
        )
        self.left_side.add(self.main_table)


        # RIGHT SIDE OF MAIN WINDOW
        self.right_side = toga.Box(
            style=Pack(direction='column')
        )
        self.right_side_buttons = toga.Box(
            style=Pack(direction='row')
        )
        self.right_side_buttons.add(toga.Button(
            "Find Duplicates",
            on_press=self.scan_dups,
            style=Pack(margin=5)
        ))
        self.right_side_buttons.add(toga.Button(
            "Hide Duplicates",
            on_press=self.hide_dups,
            style=Pack(margin=5)
        ))
        self.right_side_buttons.add(toga.Button(
            "Preferences",
            on_press=lambda widget: DedupConfig(self.game_library, self.app_config).show(),
            style=Pack(margin=5)
        ))
        self.duplicates_table = toga.Tree(
            headings=["Game", "Store"],
            accessors=["Game", "Store"],
            style=Pack(flex=1)
        )
        self.right_side.add(self.right_side_buttons, toga.Divider(), self.duplicates_table)


        # COMMANDS
        dup_group = toga.Group("Duplicates", id="duplicates")
        scan_dups_cmd = toga.Command(
            lambda command, **kwargs: (self.scan_dups(None), True)[1],
            text="Find Duplicates",
            tooltip="Scan all libraries for duplicate games",
            icon=toga.Icon(icon_path / "dup.png"),
            group=dup_group
        )
        save_library_cmd = toga.Command(
            lambda command, **kwargs: (self.save_library(None), True)[1],
            text="Save Library",
            tooltip="Save library changes to config",
            icon=toga.Icon(icon_path / "save.png"),
            group=toga.Group.APP,
            shortcut=toga.Key.MOD_1 + "s"
        )
        reset_window_cmd = toga.Command(
            lambda command, **kwargs: (setattr(self.main_window, "size", (1400, 900)), True)[1],
            text="Reset Window Size",
            tooltip="Reset the window size to default",
            group=toga.Group.WINDOW
        )
        self.commands.add(scan_dups_cmd, save_library_cmd, reset_window_cmd)
        
        # self.main_window.toolbar.add(scan_dups_cmd, save_library_cmd)
        self.split = toga.SplitContainer(direction=Direction.VERTICAL)
        self.main_window.content = self.split
        self.on_exit = self.on_close_handler
        self.main_window.show()

        # Re-apply equal flex after the window is realized so the divider starts 50/50.
        self.split.content = [
            (self.left_side, 1),
            (self.right_side, 1)
        ]
        self.refresh_library(self)

    async def on_close_handler(self, app: toga.App, **kwargs):
        width, height = self.main_window.size
        self.app_config.set_value('DEFAULT', 'window_width', str(width))
        self.app_config.set_value('DEFAULT', 'window_height', str(height))
        save_changes = toga.QuestionDialog(
            "Save Changes",
            "Do you want to save changes to your library before closing?"
        )
        ans = await self.main_window.dialog(save_changes)
        logger.info(f"Dialog answer: {ans}")
        if ans:
            self.save_library(self)
        self.exit()

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
        self.duplicates = self.game_library.get_duplicates()
        self.refresh_dups(self)

    def refresh_dups(self, widget):
        self.duplicates_table.data.clear()
        tree_data = []
        for game_dups in self.duplicates:
            if not game_dups: continue

            first_game = game_dups[0]
            parent_node = {
                "Game": f"{first_game.title} ({len(game_dups)} copies)",
                "Store": ""
            }
            children = []
            for game in game_dups:
                icon = self.hidden_icon if game.is_hidden else self.visible_icon
                child_data = {
                    "Game": (icon, f" {game.title}"),
                    "Store": game.platform
                }
                children.append((child_data, None))
            tree_data.append((parent_node, children))
        sorted_data = sorted(tree_data, key=lambda t: t[0]["Game"])
        self.duplicates_table.data = sorted_data

    async def hide_dups(self, widget):
        if not self.duplicates:
            logger.info("No duplicates to hide")
            return
        platform_priority = self.app_config.get_value('Deduplication', 'platform_priority')
        if platform_priority:
            platform_priority = platform_priority.split(",")
            logger.info(f"Using platform priority from config: {platform_priority}")
        else:
            platform_priority = list(self.game_library.platforms)
            logger.info(f"No platform priority in config, using library platforms: {platform_priority}")
        HeroicDupsHider(self.duplicates, platform_priority)
        self.refresh_library(self)
        self.refresh_dups(self)
        for node in self.duplicates_table.data:
            self.duplicates_table.expand(node)
        success = toga.InfoDialog(
            "Duplicates Hidden",
            "Duplicate games have been hidden based on your platform priority. Remember to save your library to apply changes to your config."
        )
        await self.main_window.dialog(success)


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    return HeroicLibraryManager(
        "Heroic Library Manager",
        "io.github.preppie22.heroiclibrarymanager",
    )
