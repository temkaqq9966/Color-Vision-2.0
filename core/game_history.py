
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
GAME_FILE = BASE_DIR / "data" / "game_history.json"


def load_games():
    GAME_FILE.parent.mkdir(parents=True, exist_ok=True)

    if not GAME_FILE.exists():
        GAME_FILE.write_text("[]", encoding="utf-8")

    try:
        with open(GAME_FILE, "r", encoding="utf-8") as file:
            games = json.load(file)

        if isinstance(games, list):
            return games
    except (OSError, json.JSONDecodeError):
        pass

    return []


def save_games(games):
    GAME_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(GAME_FILE, "w", encoding="utf-8") as file:
        json.dump(
            games,
            file,
            indent=4,
            ensure_ascii=False
        )


def save_game(total_score, round_scores):
    games = load_games()

    game = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_score": int(total_score),
        "max_score": 500,
        "round_scores": [int(s) for s in round_scores]
    }

    games.insert(0, game)

    save_games(games)

    return game


def delete_game(index):
    games = load_games()

    if 0 <= index < len(games):
        games.pop(index)
        save_games(games)
        return True

    return False


def clear_games():
    save_games([])


def get_best_score():
    games = load_games()
    return max(
        (int(game.get("total_score", 0)) for game in games),
        default=0
    )


def get_game_count():
    return len(load_games())
