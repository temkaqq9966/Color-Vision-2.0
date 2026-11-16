
import random
import math


def generate_color():
    return tuple(random.randint(35, 220) for _ in range(3))


def rgb_to_hex(rgb):
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def hex_to_rgb(hex_color):
    value = hex_color.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def calculate_score(target, selected):
    distance = math.sqrt(
        sum((a - b) ** 2 for a, b in zip(target, selected))
    )

    max_distance = math.sqrt(3 * (255 ** 2))
    score = round(100 * (1 - distance / max_distance))

    return max(0, min(100, score))
