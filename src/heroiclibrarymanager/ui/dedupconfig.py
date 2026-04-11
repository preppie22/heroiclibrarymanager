import toga
from toga.sources import ListSource, ListSourceT
from toga.style import Pack
import logging

from heroiclibrarymanager.core.library import GameLibrary
from heroiclibrarymanager.ui.appconfig import AppConfig

logger = logging.getLogger(__name__)

def DedupConfig(game_library: GameLibrary, app_config: AppConfig):
    platforms = list(game_library.platforms)
    window = toga.Window(title="Deduplication Config")

    platform_priority = app_config.get_value("Deduplication", "platform_priority")

    def move_up(table_view):
        logger.info(f"Moving down, current selection: {table_view.selection}")
        selected = table_view.selection
        idx = table_view.data.index(selected)
        if idx > 0:
            prior_store = table_view.data[idx-1].store
            table_view.data[idx-1] = (table_view.data[idx-1].priority, selected.store)
            table_view.data[idx] = (table_view.data[idx].priority, prior_store)

    def move_down(table_view):
        logger.info(f"Moving down, current selection: {table_view.selection}")
        selected = table_view.selection
        idx = table_view.data.index(selected)
        if idx < len(table_view.data) - 1:
            prior_store = table_view.data[idx+1].store
            table_view.data[idx+1] = (table_view.data[idx+1].priority, selected.store)
            table_view.data[idx] = (table_view.data[idx].priority, prior_store)

    main_box = toga.Column()
    store_priority = toga.Column(style=Pack(margin=10, gap=10))

    store_priority_table_buttons = toga.Column(style=Pack(gap=5, margin_top=20))
    store_priority_table_buttons.add(
        toga.Button(
        "↑",
        on_press=lambda w: move_up(store_priority_table_view)
        ),
        toga.Button(
        "↓",
        on_press=lambda w: move_down(store_priority_table_view)
        )  
    )
    store_priority_table_view = toga.Table(
        accessors=["priority", "store"],
        headings=["Priority", "Store"],
        multiple_select=False,
        style=Pack(flex=1)
    )
    for i, p in enumerate(platforms):
        store_priority_table_view.data.append((i+1,p))
    store_priority_table = toga.Row(style=Pack(gap=10))
    store_priority_table.add(store_priority_table_buttons, store_priority_table_view)
  
    store_priority.add(toga.Label("Set the priority for which store's version of a game to keep in case of duplicates:"))
    store_priority.add(store_priority_table)


    main_box.add(store_priority)
    window.content = main_box
    return window


