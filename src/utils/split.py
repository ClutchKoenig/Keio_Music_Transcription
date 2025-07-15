import os
import argparse


NB_STEMS_DEFAULT = 5
PROP_DECREASE_DEFAULT = 0.5
RMS_DEFAULT = 0.005


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split audio into stems using Spleeter.")
    parser.add_argument("file", help="Path to input audio file")
    parser.add_argument("--output", type=str, default="output/")
    parser.add_argument("--nb_stems", type=int, default=NB_STEMS_DEFAULT, 
                        help="Number of stems to separate (2, 4, or 5)")
    parser.add_argument("--prop_decrease", type=float, default=PROP_DECREASE_DEFAULT, 
                        help="Noise reduction strength (0 to 1)")
    parser.add_argument("--rms", type=float, default=RMS_DEFAULT, 
                        help="Minimum RMS to keep a stem")

    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"Error: file '{args.file}' does not exist.")
        exit(1)


import numpy as np
import librosa
import noisereduce as nr
import soundfile as sf
from spleeter.separator import Separator
from pathlib import Path 


def split_audio(
        file, 
        nb_stems=NB_STEMS_DEFAULT, 
        prop_decrease=PROP_DECREASE_DEFAULT, 
        rms=RMS_DEFAULT,
    ):
    # Load the audio file
    y_mono, sr = librosa.load(file, sr=44100, mono=True)

    # Small noise reduction
    y_denoised = nr.reduce_noise(y=y_mono, sr=sr, prop_decrease=prop_decrease)

    # Convert artificially to stereo for Spleeter
    y_stereo = np.tile(y_denoised.reshape(-1, 1), (1, 2))

    # 2 stems (vocals, accompaniment)
    # 4 stems (vocals, drums, bass, other)
    # 5 stems (piano, vocals, drums, bass, other)
    separator = Separator(f'spleeter:{nb_stems}stems', multiprocess=False) #Turned off multiprocessing as it causes problem in windows env
    prediction = separator.separate(y_stereo)
    
    ### Stems are stored in a dictionary:
    # piano = prediction['piano']
    # vocals = prediction['vocals']
    # drums = prediction['drums']
    # bass = prediction['bass']
    # other = prediction['other']

    # Remove silent stems based on RMS threshold
    stems_to_delete = []
    for stem in prediction:
        # Convert stereo to mono
        prediction[stem] = np.mean(prediction[stem], axis=1)

        rms_values = librosa.feature.rms(y=prediction[stem])
        if np.mean(rms_values) < rms:
            stems_to_delete.append(stem)

    # Delete stems that are below the RMS threshold
    for stem in stems_to_delete:
        del prediction[stem]

    return prediction


def output_split(
        input_file: str, 
        nb_stems=NB_STEMS_DEFAULT, 
        prop_decrease=PROP_DECREASE_DEFAULT, 
        rms=RMS_DEFAULT,
    ):
    prediction = split_audio(input_file, nb_stems, prop_decrease, rms)

    song_name = Path(input_file).stem
    filename = os.path.splitext(os.path.basename(input_file))[0]
    os.makedirs(args.output, exist_ok=True)

    for stem, audio in prediction.items():
        output_file = os.path.join(args.output, f"{stem}.wav")
        sf.write(output_file, audio, 44100)
        print(f"Saved {stem} stem to {output_file}")
    print("================Audio splitting completed=====================")


if __name__ == "__main__":
    output_split(args.file, args.nb_stems, args.prop_decrease, args.rms)