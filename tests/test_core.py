import logging
from pathlib import Path
import io

# logging.basicConfig(level=logging.DEBUG)

def test_scanner():
    from heroiclibrarymanager.core.scanner import HeroicScanner
    scanner = HeroicScanner(Path("tests/test_configs"))
    games = scanner.scan()

    output = io.StringIO()
    for game in games:
        output.write(f"{game}\n")

    sample_file = ""
    test_file = output.getvalue()

    with open("tests/samples/scanner_sample.txt", "r", encoding='utf-8') as f:
        sample_file = f.read()

    assert test_file == sample_file, f"Scanner output does not match sample output."

def test_environment():
    from heroiclibrarymanager.core.environment import Environment
    env = Environment()
    assert env.os_name == "Linux"