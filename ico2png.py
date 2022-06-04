import shutil
from pathlib import Path

from PIL import Image

output_dir = Path("./favicon/png")


def convert(image_file: Path):
    image = Image.open(image_file)
    png_file = output_dir.joinpath(f"{image_file.stem}.png")
    image.save(png_file)


for ico in Path("./favicon/ico").glob("*.ico"):
    convert(ico)

for ico in Path("./favicon/manual").glob("*.ico"):
    convert(ico)

for jpg in Path("./favicon/manual").glob("*.jpg"):
    convert(jpg)

for png in Path("./favicon/manual").glob("*.png"):
    shutil.copy(png, output_dir)
