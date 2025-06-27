import os
import glob
from music21 import converter, stream, instrument, metadata, environment
from PIL import Image

# === CONFIGURATION ===

# midi_paths = glob.glob("../../output/model_midi/*.mid")
midi_paths = glob.glob("../../data/*.mid")
output_prefix = "../../output/post_score/score"

us = environment.UserSettings()
us['musicxmlPath'] = '/usr/bin/mscore3'
us['musescoreDirectPNGPath'] = '/usr/bin/mscore3'

# === MIDI TREATMENT ===

full_score = stream.Score()
full_score.metadata = metadata.Metadata()
full_score.metadata.title = " + ".join([os.path.splitext(os.path.basename(f))[0] for f in midi_paths])

for midi_path in midi_paths:
    part_score = converter.parse(midi_path)

    if part_score.__class__.__name__ == "Score":
        part = part_score.parts[0]
    else:
        part = part_score

    if not any(isinstance(el, instrument.Instrument) for el in part.recurse()):
        name_guess = os.path.splitext(os.path.basename(midi_path))[0]
        part.insert(0, instrument.fromString(name_guess))

    full_score.append(part)


# === EXPORT TO PNG VIA MUSESCORE ===

os.makedirs(os.path.dirname(output_prefix), exist_ok=True)
full_score.write('musicxml.png', fp=f"{output_prefix}.png")

# === ADD WHITE BACKGROUND AND MARGINS ===

def add_margins_and_white_bg(image_path, top=20, right=60, bottom=20, left=60):
    img = Image.open(image_path).convert("RGBA")
    new_width = img.width + left + right
    new_height = img.height + top + bottom
    background = Image.new("RGBA", (new_width, new_height), (255, 255, 255, 255))
    background.paste(img, (left, top), mask=img)
    background.convert("RGB").save(image_path, "PNG")

def fix_all_images(png_prefix):
    png_files = sorted(glob.glob(f"{png_prefix}-*.png"))
    if os.path.exists(f"{png_prefix}.png"):
        png_files.insert(0, f"{png_prefix}.png")
    for path in png_files:
        add_margins_and_white_bg(path)

fix_all_images(output_prefix)