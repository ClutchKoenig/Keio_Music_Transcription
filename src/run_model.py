# import utils.split as splt
# import utils.evaluation as ev
# import utils.model_optimizer as opt
# from model.model_parameter import INSTRUMENT_PARAMS
# import model.midi_generator as midi_gen

import os, subprocess

from pathlib import Path
from src.model import midi_generator as midi_gen

# RAW_AUDIO_PATH = 'data/raw/busoni_sonata/Busoni_sonata_no2_op_8-BV_61_Scherzo.mp3'
# PRED_MIDI_PATH = 'output/model_midi/Busoni_sonata_no2_op_8-BV_61_Scherzo_basic_pitch.mid'
# GT_MIDI_PATH = 'data/raw/busoni_sonata/Busoni_sonata_no2_op_8-BV_61_Scherzo.mid'
# TMP_PRED_MIDI_PATH = 'output/model_midi/tmp_pred.mid'


def process_audio(audio_file, output_path, format):
    stem_dir = os.path.join(output_path, "stems")
    midi_dir = os.path.join(output_path, "midi")
    score_dir = os.path.join(output_path, "score")

    os.makedirs(stem_dir, exist_ok=True)
    os.makedirs(midi_dir, exist_ok=True)
    os.makedirs(score_dir, exist_ok=True)

    '''
    Split the main audio into seperate instrument stems
    '''
    #stems = splt.split_audio(audio_file)
    subprocess.run([
        "/content/music_venv310/bin/python", 
        "src/utils/split.py", 
        audio_file, 
        "--output", stem_dir
    ], check=True)

    # import tensorflow as tf
    # tf.keras.backend.clear_session()
    for wav_path in stem_dir.iterdir():
        name = Path(wav_path).stem
        print(f"Predicting MidiFile for:{name}")
        '''
        Iterate over all stems and generate .mid + score
        '''
        #wav_path = stem_dir / f"{name}.wav"
        #sf.write(wav_path, wav, 44100)

        # Generate MIDI file for this stem
        midi_gen.transcribe_with_optimal_params(
            wav_path=str(wav_path),
            output_dir=str(midi_dir)
        )

    # TODO: Generate score from MIDI and save in `score_dir`


if __name__=='__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=str, help='Path to the input audio file')
    parser.add_argument('--output', type=str, required=False, default='output/')
    parser.add_argument('--format', type=str, choices=['midi', 'pdf'], required=False, default='midi')
    args = parser.parse_args()

    process_audio(args.input, args.output, args.format)
