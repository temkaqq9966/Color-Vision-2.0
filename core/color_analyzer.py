from __future__ import annotations

import colorsys
from typing import TypeAlias

RGB: TypeAlias = tuple[int, int, int]


def parse_color(value: str | tuple[int, int, int] | list[int]) -> RGB:
    """Parse a #RGB/#RRGGBB string or an RGB sequence."""
    if isinstance(value, str):
        text = value.strip()
        if text.startswith("#"):
            text = text[1:]
        if len(text) == 3:
            text = "".join(character * 2 for character in text)
        if len(text) != 6:
            raise ValueError("Color must use #RGB or #RRGGBB format.")
        try:
            channels = tuple(int(text[index:index + 2], 16) for index in (0, 2, 4))
        except ValueError as error:
            raise ValueError("Color contains a non-hexadecimal character.") from error
    elif isinstance(value, (tuple, list)) and len(value) == 3:
        channels = tuple(value)
    else:
        raise ValueError("Color must be a hex string or three RGB channels.")

    if any(not isinstance(channel, int) or not 0 <= channel <= 255 for channel in channels):
        raise ValueError("RGB channels must be integers between 0 and 255.")
    return channels  # type: ignore[return-value]


def to_hex(rgb: RGB) -> str:
    red, green, blue = parse_color(rgb)
    return f"#{red:02X}{green:02X}{blue:02X}"


def _linearize(channel: int) -> float:
    value = channel / 255
    return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4


def relative_luminance(rgb: RGB) -> float:
    red, green, blue = parse_color(rgb)
    return (
        0.2126 * _linearize(red)
        + 0.7152 * _linearize(green)
        + 0.0722 * _linearize(blue)
    )


def contrast_ratio(first: RGB, second: RGB) -> float:
    luminances = sorted((relative_luminance(first), relative_luminance(second)))
    return (luminances[1] + 0.05) / (luminances[0] + 0.05)


def analyze_color(rgb: RGB) -> dict[str, object]:
    red, green, blue = parse_color(rgb)
    hue, saturation, lightness = colorsys.rgb_to_hls(
        red / 255, green / 255, blue / 255
    )
    return {
        "rgb": (red, green, blue),
        "hex": to_hex((red, green, blue)),
        "hue_degrees": round(hue * 360),
        "saturation_percent": round(saturation * 100),
        "lightness_percent": round(lightness * 100),
        "luminance": round(relative_luminance((red, green, blue)), 4),
        "complementary_hex": to_hex((255 - red, 255 - green, 255 - blue)),
        "contrast_with_white": round(contrast_ratio((red, green, blue), (255, 255, 255)), 2),
        "contrast_with_black": round(contrast_ratio((red, green, blue), (0, 0, 0)), 2),
    }