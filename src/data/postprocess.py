import os
import glob
from music21 import converter, stream, instrument, metadata, environment, tempo
from PIL import Image
import subprocess

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


def pngs_to_pdf(png_dir, pdf_path, png_prefix="score"):
    png_prefix = os.path.join(png_dir, png_prefix)
    png_files = sorted(glob.glob(f"{png_prefix}*.png"))

    images = [Image.open(f).convert("RGB") for f in png_files]

    first_image = images[0]
    other_images = images[1:]

    first_image.save(
        pdf_path, save_all=True, append_images=other_images
    )


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
    # ================= Convert to PDF directly via musicxml=============
    # os.makedirs(output_dir, exist_ok=True)
    # output_path = os.path.join(output_dir, "score.png")
    # score.write('musicxml.png', fp=output_path)

    # fix_all_images(output_dir)

    # output_pdf = os.path.join(output_dir, "score.pdf")
    # pngs_to_pdf(output_dir, output_pdf)
    # fix_all_images()
    # ======================================================================
    musicxml_path = os.path.join(output_dir, "score.musicxml")
    score.write('musicxml', fp=musicxml_path)

    # Call MuseScore via CLI to convert XML to PDF without GUI
    pdf_path = os.path.join(output_dir, "score.pdf")
    try:
        subprocess.run(['xvfb-run', '--auto-servernum', '--server-args=-screen 0 640x480x24',str(us['musicxmlPath']), musicxml_path, '-o', pdf_path], check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"MuseScore PDF generation failed:\n{e}")
    

def multi_midi_treatment(midi_files, output_dir):
    us = environment.UserSettings()
    us['musicxmlPath'] = '/usr/bin/mscore3'
    us['musescoreDirectPNGPath'] = '/usr/bin/mscore3'

    full_score = stream.Score()
    full_score.metadata = metadata.Metadata()
    full_score.metadata.title = " + ".join([os.path.splitext(os.path.basename(f))[0] for f in midi_files])

    for midi_path in midi_files:
        part_score = converter.parse(midi_path)
        if part_score.__class__.__name__ == "Score":
            part = part_score.parts[0]
        else:
            part = part_score

        if not any(isinstance(el, instrument.Instrument) for el in part.recurse()):
            name_guess = os.path.splitext(os.path.basename(midi_path))[0]
            part.insert(0, instrument.fromString(name_guess))

        full_score.append(part)

    tempi = list(full_score.recurse().getElementsByClass(tempo.MetronomeMark))
    if len(tempi) > 1:
        for tm in tempi[1:]:
            parent = tm.getContextByClass('Measure')
            if parent:
                parent.remove(tm)
            else:
                tm.activeSite.remove(tm)

    musicxml_path = os.path.join(output_dir, "score.musicxml")
    full_score.write('musicxml', fp=musicxml_path)

    # Call MuseScore via CLI to convert XML to PDF without GUI
    pdf_path = os.path.join(output_dir, "score.pdf")
    try:
        subprocess.run(['xvfb-run', '--auto-servernum', '--server-args=-screen 0 640x480x24',str(us['musicxmlPath']), musicxml_path, '-o', pdf_path], check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"MuseScore PDF generation failed:\n{e}")