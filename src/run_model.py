import utils.split as splt
import utils.evaluation as ev
import utils.model_optimizer as opt


RAW_AUDIO_PATH = 'data/raw/busoni_sonata/Busoni_sonata_no2_op_8-BV_61_Scherzo.mp3'
PRED_MIDI_PATH = 'output/model_midi/Busoni_sonata_no2_op_8-BV_61_Scherzo_basic_pitch.mid'
GT_MIDI_PATH = 'data/raw/busoni_sonata/Busoni_sonata_no2_op_8-BV_61_Scherzo.mid'
TMP_PRED_MIDI_PATH = 'output/model_midi/tmp_pred.mid'


###    TEMP    ###

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--input', type=str, required=True)
parser.add_argument('--output', type=str, required=True)
parser.add_argument('--format', type=str, choices=['midi', 'pdf'], required=True)
args = parser.parse_args()

# Exemple : traitement à adapter selon ton modèle
print(f"Traitement du fichier {args.input} vers {args.output} au format {args.format}")

# Simulate waiting time
import time
time.sleep(2)

# simulate conversion
with open(args.output, 'w') as f:
    f.write("converted content")

###    TEMP    ###