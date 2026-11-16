
import cv2
import numpy as np

from core.color_matcher import find_custom_color


def rgb_to_hex(rgb):
    return "#{:02X}{:02X}{:02X}".format(
        *[int(value) for value in rgb]
    )


def get_basic_color_name(h, s, v):
    h = int(h)
    s = int(s)
    v = int(v)

    # Хар, цагаан, саарал
    if v < 45:
        return "Black"

    if s < 30:
        if v >= 220:
            return "White"
        if v < 100:
            return "Dark Gray"
        if v >= 170:
            return "Light Gray"
        return "Gray"

    # Өнгө маш бараан үед
    if v < 85:
        return "Dark Color"

    # HSV Hue: OpenCV дээр 0-179
    if h < 10 or h >= 175:
        name = "Red"
    elif h < 20:
        name = "Orange"
    elif h < 35:
        name = "Yellow"
    elif h < 45:
        name = "Yellow Green"
    elif h < 85:
        name = "Green"
    elif h < 100:
        name = "Cyan"
    elif h < 130:
        name = "Blue"
    elif h < 150:
        name = "Purple"
    elif h < 175:
        name = "Pink"
    else:
        name = "Red"

    if s < 65:
        return "Pale " + name

    if v < 140:
        return "Dark " + name

    if v > 215 and s < 120:
        return "Light " + name

    return name


def analyze_region(frame, x, y, size=25):
    height, width = frame.shape[:2]

    x = max(0, min(int(x), width - 1))
    y = max(0, min(int(y), height - 1))

    radius = max(1, size // 2)

    x1 = max(0, x - radius)
    x2 = min(width, x + radius + 1)

    y1 = max(0, y - radius)
    y2 = min(height, y + radius + 1)

    region = frame[y1:y2, x1:x2]

    # BGR -> RGB
    rgb_region = cv2.cvtColor(
        region,
        cv2.COLOR_BGR2RGB
    )

    # Median ашиглаж шуугианыг багасгана
    median_rgb = np.median(
        rgb_region.reshape(-1, 3),
        axis=0
    ).astype(np.uint8)

    rgb = tuple(
        int(value) for value in median_rgb
    )

    hsv_pixel = cv2.cvtColor(
        np.uint8([[rgb]]),
        cv2.COLOR_RGB2HSV
    )[0, 0]

    h, s, v = (
        int(value) for value in hsv_pixel
    )

    custom_name = find_custom_color(rgb)

    if custom_name:
        name = custom_name
        source = "Saved Color"
    else:
        name = get_basic_color_name(h, s, v)
        source = "Automatic"

    return {
        "name": name,
        "rgb": rgb,
        "hex": rgb_to_hex(rgb),
        "hsv": (h, s, v),
        "source": source,
        "region": (x1, y1, x2, y2)
    }


def detect_center_color(frame):
    height, width = frame.shape[:2]

    return analyze_region(
        frame,
        width // 2,
        height // 2,
        size=50
    )


def detect_point_color(frame, x, y):
    return analyze_region(
        frame,
        x,
        y,
        size=25
    )
