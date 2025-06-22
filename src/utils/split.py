import sys
import os

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_spleeter.py <filename>")
        sys.exit(1)
    file = sys.argv[1]
    if not os.path.exists(file):
        print(f"File '{file}' does not exist in input directory.")
        sys.exit(1)

from spleeter.separator import Separator
import numpy as np
import librosa
import noisereduce as nr
import soundfile as sf

def split_audio(file, nb_stems=5, prop_decrease=0.5):
    # Load the audio file
    y_mono, sr = librosa.load(file, sr=44100, mono=True)

    # Small noise reduction
    y_denoised = nr.reduce_noise(y=y_mono, sr=sr, prop_decrease=prop_decrease)

    # Convert artificially to stereo for Spleeter
    y_stereo = np.tile(y_denoised.reshape(-1, 1), (1, 2))

    # 2 stems (vocals, accompaniment)
    # 4 stems (vocals, drums, bass, other)
    # 5 stems (piano, vocals, drums, bass, other)
    separator = Separator(f'spleeter:{nb_stems}stems')
    prediction = separator.separate(y_stereo)

    ### Stems are stored in a dictionary:
    # piano = prediction['piano']
    # vocals = prediction['vocals']
    # drums = prediction['drums']
    # bass = prediction['bass']
    # other = prediction['other']

    return prediction

if __name__ == "__main__":
    prediction = split_audio(file)
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    for stem, audio in prediction.items():
        output_file = os.path.join(output_dir, f"{os.path.splitext(file)[0]}_{stem}.wav")
        sf.write(output_file, audio, 44100)
        print(f"Saved {stem} stem to {output_file}")
    print("Audio splitting completed.")
    print("Output files are stored in the 'output' directory.")