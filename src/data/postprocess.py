import os
import glob
from music21 import converter, stream, instrument, metadata, environment, tempo
from PIL import Image


def add_margins_and_white_bg(image_path, top=20, right=60, bottom=20, left=60):
    img = Image.open(image_path).convert("RGBA")
    new_width = img.width + left + right
    new_height = img.height + top + bottom
    background = Image.new("RGBA", (new_width, new_height), (255, 255, 255, 255))
    background.paste(img, (left, top), mask=img)
    background.convert("RGB").save(image_path, "PNG")


def fix_all_images(output_dir, png_prefix="score"):
    png_prefix = os.path.join(output_dir, png_prefix)
    png_files = sorted(glob.glob(f"{png_prefix}-*.png"))
    if os.path.exists(f"{png_prefix}.png"):
        png_files.insert(0, f"{png_prefix}.png")
    for path in png_files:
        add_margins_and_white_bg(path)


def midi_treatment(midi_file, output_dir):
    us = environment.UserSettings()
    us['musicxmlPath'] = '/usr/bin/mscore3'
    us['musescoreDirectPNGPath'] = '/usr/bin/mscore3'

    score = converter.parse(midi_file)

    tempi = list(score.recurse().getElementsByClass(tempo.MetronomeMark))
    if len(tempi) > 1:
        for tm in tempi[1:]:
            parent = tm.getContextByClass('Measure')
            if parent:
                parent.remove(tm)
            else:
                tm.activeSite.remove(tm)

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "score.png")
    score.write('musicxml.png', fp=output_path)

    fix_all_images(output_dir)
