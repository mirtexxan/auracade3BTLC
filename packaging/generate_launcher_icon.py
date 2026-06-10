from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageFilter


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCE_IMAGE = PROJECT_ROOT / "games" / "Alom" / "musci.png"
OUTPUT_ICON = PROJECT_ROOT / "packaging" / "icons" / "auracade_alom.ico"
CANVAS_SIZE = 256


def main() -> int:
    if not SOURCE_IMAGE.exists():
        raise SystemExit(f"Sorgente icona non trovata: {SOURCE_IMAGE}")

    OUTPUT_ICON.parent.mkdir(parents=True, exist_ok=True)

    source = Image.open(SOURCE_IMAGE).convert("RGBA")
    bounds = source.getbbox()
    if bounds:
        source = source.crop(bounds)

    source.thumbnail((CANVAS_SIZE - 28, CANVAS_SIZE - 28), Image.Resampling.LANCZOS)

    canvas = Image.new("RGBA", (CANVAS_SIZE, CANVAS_SIZE), (0, 0, 0, 0))
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))

    offset_x = (CANVAS_SIZE - source.width) // 2
    offset_y = CANVAS_SIZE - source.height - 8
    shadow.alpha_composite(source, (offset_x + 6, offset_y + 8))
    shadow = shadow.filter(ImageFilter.GaussianBlur(8))
    shadow.putalpha(shadow.getchannel("A").point(lambda value: value * 0.4))

    canvas.alpha_composite(shadow)
    canvas.alpha_composite(source, (offset_x, offset_y))

    sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    canvas.save(OUTPUT_ICON, format="ICO", sizes=sizes)
    print(OUTPUT_ICON)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
