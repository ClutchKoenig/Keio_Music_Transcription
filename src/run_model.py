# import utils.split as splt
# import utils.evaluation as ev
# import utils.model_optimizer as opt
# from model.model_parameter import INSTRUMENT_PARAMS
# import model.midi_generator as midi_gen
import os
import sys
sys.path.append(os.path.abspath('./src'))

import soundfile as sf
from utils import split as splt
from utils import evaluation as ev
from utils import model_optimizer as opt
from model import midi_generator as midi_gen
from model.model_parameter import  INSTRUMENT_PARAMS
from basic_pitch.inference import Model
from basic_pitch import ICASSP_2022_MODEL_PATH

import os
from pathlib import Path

import subprocess
# RAW_AUDIO_PATH = 'data/raw/busoni_sonata/Busoni_sonata_no2_op_8-BV_61_Scherzo.mp3'
# PRED_MIDI_PATH = 'output/model_midi/Busoni_sonata_no2_op_8-BV_61_Scherzo_basic_pitch.mid'
# GT_MIDI_PATH = 'data/raw/busoni_sonata/Busoni_sonata_no2_op_8-BV_61_Scherzo.mid'
# TMP_PRED_MIDI_PATH = 'output/model_midi/tmp_pred.mid'


###    TEMP    ###

# import argparse

# parser = argparse.ArgumentParser()
# parser.add_argument('--input', type=str, required=True)
# parser.add_argument('--output', type=str, required=True)
# parser.add_argument('--format', type=str, choices=['midi', 'pdf'], required=True)
# args = parser.parse_args()

# # Exemple : traitement à adapter selon ton modèle
# print(f"Traitement du fichier {args.input} vers {args.output} au format {args.format}")

# # Simulate waiting time
# import time
# time.sleep(2)

# # simulate conversion
# with open(args.output, 'w') as f:
#     f.write("converted content")

###    TEMP    ###
# BELOW IS ADDED THE STANDARD RUN PROCEDURE============================================================================
if __name__=='__main__':
    
    audio_file = 'song_name.mp3' # Here the string should be replaced using the input parser

    base_name = Path(audio_file).stem  # → "song_name"
    output_base = Path("output") / base_name
    stem_dir = output_base / "stems"
    midi_dir = output_base / "midi"
    score_dir = output_base / "score"

    os.makedirs(stem_dir, exist_ok=True)
    os.makedirs(midi_dir, exist_ok=True)
    os.makedirs(score_dir, exist_ok=True)

    '''
    Split the main audio into seperate instrument stems
    '''
    stems = splt.split_audio(audio_file)
    subprocess.run(["/content/music_venv310/bin/python", "src/utils/split.py", audio_file], check=True)

    # import tensorflow as tf
    # tf.keras.backend.clear_session()
    for name, wav in stems.items():
        '''
        Iterate over all stems and generate .mid + score
        '''
        wav_path = stem_dir / f"{name}.wav"
        sf.write(wav_path, wav, 44100)

        # Generate MIDI file for this stem
        midi_gen.transcribe_with_optimal_params(
            wav_path=str(wav_path),
            output_dir=str(midi_dir)
        )

        # TODO: Generate score from MIDI and save in `score_dir`