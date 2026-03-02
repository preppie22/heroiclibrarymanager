"""
Manages duplicate games from multiple stores in Heroic Games Launcher.
"""

import toga
from toga.style import Pack

from heroiclibrarymanager.core.scanner import HeroicScanner
from heroiclibrarymanager.core.library import GameLibrary
# from heroiclibrarymanager.core.environment import Environment

class HeroicLibraryManager(toga.App):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config_path = "/workspaces/heroiclibrarymanager/tests/test_configs"
        self.game_library = GameLibrary(HeroicScanner(self.config_path).scan())

    def startup(self):
        icon_path = self.paths.app / "resources" / "icons"
        self.hidden_icon = toga.Icon(icon_path / "hidden.png")
        self.visible_icon = toga.Icon(icon_path / "visible.png")
        self.library_icon = toga.Icon(icon_path / "library.png")
        self.dup_icon = toga.Icon(icon_path / "dup.png")
        print(icon_path)
        # main_box = toga.Box()

        # added a hint here because the studid linter keeps showing red squigglies
        self.main_window: toga.MainWindow = toga.MainWindow(title=self.formal_name)

        self.main_table = toga.DetailedList(style=Pack(flex=1))
        self.duplicates_table = toga.Tree(
            headings=["Game", "Store"],
            accessors=["Game", "Store"]
        )

        scan_cmd = toga.Command(
            self.scan_library,
            text="Reload Libraries",
            tooltip="Rescan all store libraries",
            icon=self.library_icon,
        )
        scan_dups_cmd = toga.Command(
            self.scan_dups,
            text="Find Duplicates",
            tooltip="Scan all libraries for duplicate games",
            icon=self.dup_icon
        )

        self.main_window.toolbar.add(scan_cmd)
        self.main_window.toolbar.add(scan_dups_cmd)
        split = toga.SplitContainer()
        split.content = [self.main_table, self.duplicates_table]

        self.main_window.content = split
        self.main_window.show()
        self.scan_library(self)
        # main_box.add(game_table)
        

    def scan_library(self, widget):
        self.main_table.data.clear()
        for game in self.game_library:
            if game.is_hidden:
                self.main_table.data.append({
                    "icon": self.hidden_icon,
                    "title": f" {game.title}",
                    "subtitle": f"Hidden on {game.platform}"
                })
            else:
                self.main_table.data.append({
                    "icon": self.visible_icon,
                    "title": game.title,
                    "subtitle": game.platform
                })

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
                    "Game": game.title,
                    "Store": game.platform
                }
                children.append((child_data, None))
            tree_data.append((parent_node, children))
        self.duplicates_table.data = tree_data
            
def main():
    return HeroicLibraryManager(
        "Heroic Library Manager",
        "io.github.preppie22.heroiclibrarymanager",
    )
