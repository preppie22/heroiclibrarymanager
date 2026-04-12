import toga
from toga.style import Pack
import logging
from enum import Enum

import gi 
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from heroiclibrarymanager.core.library import GameLibrary
from heroiclibrarymanager.ui.appconfig import AppConfig

logger = logging.getLogger(__name__)

def DedupConfig(game_library: GameLibrary, app_config: AppConfig):
    window = toga.Window(
        title="Deduplication Config",
        size=(300, 400)
    )

    platform_priority = app_config.get_value("Deduplication", "platform_priority")
    if platform_priority is None or platform_priority == "":
        platforms = list(game_library.platforms)
        platform_priority = ",".join(platforms)
        app_config.set_value("Deduplication", "platform_priority", platform_priority)

    def save_close(table_view):
        platforms = [row.store for row in table_view.data]
        new_platform_order = ",".join(platforms)
        app_config.set_value("Deduplication", "platform_priority", new_platform_order)
        window.close()

    class direction(Enum):
        UP = 1
        DOWN = 2

    def move_selection(table_view, direction: direction):
        selected = table_view.selection
        if selected is None:
            return
        idx = table_view.data.index(selected)

        move_idx = -1 if direction == direction.UP else 1
        check_idx = idx > 0 if direction == direction.UP else idx < len(table_view.data) - 1
        if check_idx:
            rows = [row.store for row in table_view.data]
            rows[idx], rows[idx + move_idx] = rows[idx + move_idx], rows[idx]
            table_view.data.clear()
            for row in rows:
                table_view.data.append((row,))

            # very hacky way to reselect moved item because toga doesn't provide a way to do it directly
            # does NOT work on Windows!
            scrolled_window = table_view._impl.native
            tree_view = scrolled_window.get_child()
            selection = tree_view.get_selection()
            selection.select_path((idx + move_idx,))
            tree_view.grab_focus()

    main_box = toga.Column(style=Pack(margin=10, gap=10, flex=1))

    store_priority = toga.Column(style=Pack(gap=10, flex=1))
    table_buttons = toga.Column(style=Pack(gap=5, margin_top=20))
    table_buttons.add(
        toga.Button(
        "↑",
        on_press=lambda w: move_selection(store_table_view, direction.UP)
        ),
        toga.Button(
        "↓",
        on_press=lambda w: move_selection(store_table_view, direction.DOWN)
        )  
    )

    priority_table_view = toga.Table(
        accessors=["priority"],
        headings=["#"],
        multiple_select=False,
        style=Pack(width=36)
    )
    priority_table_view._impl.selection.set_mode(Gtk.SelectionMode.NONE)
    priority_table_view._impl.native_table.set_can_focus(False)
    store_table_view = toga.Table(
        accessors=["store"],
        headings=["Store"],
        multiple_select=False,
        style=Pack(flex=1)
    )
    platform_ordered_list = platform_priority.split(",")
    for i, p in enumerate(platform_ordered_list):
        priority_table_view.data.append((i + 1,))
        store_table_view.data.append((p,))

    store_priority_table = toga.Row(style=Pack(gap=10, flex=1))
    store_priority_table.add(table_buttons, priority_table_view, store_table_view)
  
    store_priority.add(toga.Label("Set the priority for which store's version of a game to keep in case of duplicates:"))
    store_priority.add(store_priority_table)

    save_close_buttons = toga.Row(style=Pack(gap=10, margin_top=10))
    save_close_buttons.add(
        toga.Box(style=Pack(flex=1)),
        toga.Button("Save & Close", on_press=lambda w: save_close(store_table_view)),
        toga.Button("Cancel", on_press=lambda w: window.close())
    )

    main_box.add(store_priority)
    main_box.add(toga.Divider())
    main_box.add(save_close_buttons)
    window.content = main_box
    return window


