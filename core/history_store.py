
import json
from pathlib import Path
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parent.parent
HISTORY_FILE = BASE_DIR / "data" / "history.json"

MAX_HISTORY = 500


def load_history():
    HISTORY_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if not HISTORY_FILE.exists():
        HISTORY_FILE.write_text(
            "[]",
            encoding="utf-8"
        )

    try:
        with open(
            HISTORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

    except (OSError, json.JSONDecodeError):
        pass

    return []


def save_history(history):
    HISTORY_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        HISTORY_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            history,
            file,
            ensure_ascii=False,
            indent=4
        )


def add_history(name, rgb, source="Camera"):
    history = load_history()

    rgb = [int(value) for value in rgb]

    entry = {
        "id": datetime.now().strftime(
            "%Y%m%d%H%M%S%f"
        ),
        "name": str(name),
        "rgb": rgb,
        "hex": "#{:02X}{:02X}{:02X}".format(*rgb),
        "source": source,
        "timestamp": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    }

    history.insert(0, entry)

    save_history(history[:MAX_HISTORY])

    return entry


def delete_history(index):
    history = load_history()

    if 0 <= index < len(history):
        history.pop(index)
        save_history(history)
        return True

    return False


def clear_history():
    save_history([])

