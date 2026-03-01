"""
Manages duplicate games from multiple stores in Heroic Games Launcher.
"""

import toga
import os
import asyncio
from toga.style import Pack

from heroiclibrarymanager.core.scanner import HeroicScanner
from heroiclibrarymanager.core.library import GameLibrary
from heroiclibrarymanager.core.environment import Environment

class HeroicLibraryManager(toga.App):
    def startup(self):
        icon_path = self.paths.app / "resources" / "icons"
        self.hidden_icon = toga.Icon(icon_path / "hidden.png")
        self.visible_icon = toga.Icon(icon_path / "visible.png")
        print(icon_path)
        # main_box = toga.Box()

        env = Environment()
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.show()
        async def check_environment(app):
             if not env.is_os_supported():
                await self.main_window.error_dialog(
                    "Unsupported OS", 
                    "Heroic Library Manager only supports Linux."
                )
                self.exit()
        self.add_background_task(check_environment)


        games = HeroicScanner("/workspaces/heroiclibrarymanager/tests/test_configs").scan()
        library = GameLibrary(games)

        main_table = toga.DetailedList(style=Pack(flex=1))
        for game in games:
            if game.is_hidden:
                main_table.data.append({
                    "icon": self.hidden_icon,
                    "title": f" {game.title}",
                    "subtitle": f"Hidden on {game.platform}"
                })
            else:
                main_table.data.append({
                    "icon": self.visible_icon,
                    "title": game.title,
                    "subtitle": game.platform
                })
        duplicates_table = toga.Table(headings=["Game", "Store"])
        for game_dups in library.get_duplicates():
            for game in game_dups:
                duplicates_table.data.append([game.title, game.platform])

        # main_box.add(game_table)
        split = toga.SplitContainer()
        split.content = [(main_table,1),(duplicates_table,1)]


        self.main_window.content = split





def main():
    return HeroicLibraryManager(
        "Heroic Library Manager",
        "io.github.preppie22.heroiclibrarymanager",
    )
