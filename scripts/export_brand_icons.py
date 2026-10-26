"""Export Hoop Roulette app icons from the brand mark's geometric construction.

Requires Pillow for asset generation only; the game has no Pillow dependency.
"""

from pathlib import Path

from PIL import Image, ImageDraw


def main() -> None:
    scale = 16
    image = Image.new("RGBA", (128 * scale, 128 * scale))
    draw = ImageDraw.Draw(image)
    ink, orange, cream = "#07111f", "#ff641f", "#f4f0e6"

    def box(values):
        return tuple(round(value * scale) for value in values)

    draw.rounded_rectangle(box((0, 0, 128, 128)), 28 * scale, fill=ink)
    draw.ellipse(box((18, 18, 110, 110)), fill=orange)
    draw.line(box((18, 64, 110, 64)), fill=ink, width=6 * scale)
    draw.line(box((64, 18, 64, 110)), fill=ink, width=6 * scale)
    for start, control in ((35, 65), (93, 63)):
        points = []
        for step in range(101):
            t = step / 100
            x = (1-t)**3*start + 3*(1-t)**2*t*control + 3*(1-t)*t*t*control + t**3*start
            y = (1-t)**3*28 + 3*(1-t)**2*t*47 + 3*(1-t)*t*t*81 + t**3*100
            points.append((round(x * scale), round(y * scale)))
        draw.line(points, fill=ink, width=6 * scale, joint="curve")
        for x, y in points:
            draw.ellipse((x-3*scale, y-3*scale, x+3*scale, y+3*scale), fill=ink)
    for x, y in ((43, 48), (85, 48), (64, 85)):
        draw.ellipse(box((x-11, y-11, x+11, y+11)), fill=ink)
        draw.ellipse(box((x-7, y-7, x+7, y+7)), fill=cream)

    image = image.resize((1024, 1024), Image.Resampling.LANCZOS)
    directory = Path(__file__).resolve().parent.parent / "web" / "static"
    image.save(directory / "app-icon.png")
    image.save(directory / "app-icon.ico", sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])
    image.save(directory / "app-icon.icns")


if __name__ == "__main__":
    main()
