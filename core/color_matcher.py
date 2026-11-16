
import json
import math
from pathlib import Path

import cv2
import numpy as np


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "colors.json"

MATCH_THRESHOLD = 12.0

# Cache
_cached_colors = None
_cached_signature = None
_cached_lab = []


def ensure_file():
    DATA_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if not DATA_FILE.exists():
        DATA_FILE.write_text(
            "[]",
            encoding="utf-8"
        )


def file_signature():
    ensure_file()

    stat = DATA_FILE.stat()

    return (
        stat.st_mtime_ns,
        stat.st_size
    )


def rgb_to_lab(rgb):
    rgb = tuple(int(v) for v in rgb)

    array = np.array(
        [[rgb]],
        dtype=np.uint8
    )

    lab = cv2.cvtColor(
        array,
        cv2.COLOR_RGB2LAB
    )[0, 0]

    return (
        float(lab[0]) * 100 / 255,
        float(lab[1]) - 128,
        float(lab[2]) - 128
    )


def color_distance(rgb1, rgb2):
    lab1 = rgb_to_lab(rgb1)
    lab2 = rgb_to_lab(rgb2)

    return math.sqrt(
        sum(
            (a - b) ** 2
            for a, b in zip(lab1, lab2)
        )
    )


def rebuild_lab_cache():
    global _cached_lab

    _cached_lab = []

    for color in _cached_colors:
        rgb = color.get("rgb")

        if not isinstance(rgb, (list, tuple)):
            continue

        if len(rgb) != 3:
            continue

        try:
            values = tuple(
                int(value) for value in rgb
            )

            if any(
                value < 0 or value > 255
                for value in values
            ):
                continue

            lab = rgb_to_lab(values)

            _cached_lab.append(
                {
                    "name": color.get(
                        "name",
                        "Unnamed"
                    ),
                    "lab": lab
                }
            )

        except (ValueError, TypeError):
            continue


def load_colors():
    global _cached_colors
    global _cached_signature

    signature = file_signature()

    if (
        _cached_colors is not None
        and signature == _cached_signature
    ):
        return [
            dict(color)
            for color in _cached_colors
        ]

    try:
        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            colors = json.load(file)

        if not isinstance(colors, list):
            colors = []

    except (OSError, json.JSONDecodeError):
        colors = []

    _cached_colors = colors
    _cached_signature = signature

    rebuild_lab_cache()

    return [
        dict(color)
        for color in _cached_colors
    ]


def save_colors(colors):
    global _cached_colors
    global _cached_signature

    ensure_file()

    with open(
        DATA_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            colors,
            file,
            ensure_ascii=False,
            indent=4
        )

    _cached_colors = [
        dict(color)
        for color in colors
    ]

    _cached_signature = file_signature()

    rebuild_lab_cache()


def add_custom_color(name, rgb):
    name = name.strip()

    if not name:
        return False

    try:
        rgb = tuple(
            int(value) for value in rgb
        )

        if len(rgb) != 3:
            return False

        if any(
            value < 0 or value > 255
            for value in rgb
        ):
            return False

    except (TypeError, ValueError):
        return False

    colors = load_colors()

    new_color = {
        "name": name,
        "rgb": list(rgb),
        "hex": "#{:02X}{:02X}{:02X}".format(
            *rgb
        )
    }

    colors.append(new_color)

    save_colors(colors)

    return True


def find_custom_color(rgb):
    load_colors()

    if not _cached_lab:
        return None

    try:
        target_lab = rgb_to_lab(rgb)

    except (ValueError, TypeError):
        return None

    best_name = None
    best_distance = float("inf")

    for saved_color in _cached_lab:
        saved_lab = saved_color["lab"]

        distance = math.sqrt(
            sum(
                (a - b) ** 2
                for a, b in zip(
                    target_lab,
                    saved_lab
                )
            )
        )

        if distance < best_distance:
            best_distance = distance
            best_name = saved_color["name"]

    if best_distance <= MATCH_THRESHOLD:
        return best_name

    return None
