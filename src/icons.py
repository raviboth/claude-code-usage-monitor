import sys

from PIL import Image, ImageDraw, ImageFont

from src.utils import color_for_utilization, format_utilization_label

# macOS menu bar icons should be 22pt, rendered at 2x for Retina = 44px
# Linux icons are typically 24px
_RENDER_SIZE = 44 if sys.platform == "darwin" else 48

# Dark background color for the inner circle of the ring
_BG_COLOR = "#1a1a1a"


def render_tray_icon(utilization: float | None) -> Image.Image:
    """Render a tray icon showing the usage percentage inside a colored ring.

    Draws a colored annulus (green/yellow/red) with a dark interior and
    white text centered inside. Returns an image at 2x resolution for
    Retina support (44x44 on macOS).
    """
    size = _RENDER_SIZE
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    color = color_for_utilization(utilization)

    # Draw outer colored circle (the ring)
    draw.ellipse([1, 1, size - 2, size - 2], fill=color)

    # Draw inner dark circle to create the ring/annulus effect
    # Ring thickness is ~16% of icon size
    ring_thickness = round(size * 0.16)
    inset = 1 + ring_thickness
    draw.ellipse(
        [inset, inset, size - 1 - ring_thickness, size - 1 - ring_thickness],
        fill=_BG_COLOR,
    )

    label = format_utilization_label(utilization)

    # Font size proportional to icon, smaller for longer text
    if len(label) <= 2:
        font_size = size * 55 // 100
    elif len(label) == 3:
        font_size = size * 42 // 100
    else:
        font_size = size * 32 // 100

    font = None
    font_paths = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFCompact.ttf",
        "/System/Library/Fonts/SFNSMono.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    for path in font_paths:
        try:
            font = ImageFont.truetype(path, font_size)
            break
        except (OSError, AttributeError):
            continue
    if font is None:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), label, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (size - text_w) // 2
    y = (size - text_h) // 2 - bbox[1]

    draw.text((x, y), label, fill="white", font=font)

    return img
