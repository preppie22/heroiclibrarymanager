import logging
from pathlib import Path

from heroiclibrarymanager.core.scanner import HeroicScanner

# logging.basicConfig(level=logging.DEBUG)

scanner = HeroicScanner(Path("tests/test_configs"))
games = scanner.scan()

with open("test_output.txt", "w", encoding="utf-8") as f:
    for game in games:
        f.write(f"{game}\n")