import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import optuna
from optuna import Trial
from optuna.samplers import TPESampler  
import model.midi_generator
import evaluation
import midi_loading


# RAW_AUDIO_PATH = 'data/raw/OMORI_cleaner/OMORI_cleaner.mp3'
# PRED_MIDI_PATH = 'output/model_midi/OMORI_cleaner.mid'
# GT_MIDI_PATH = 'data/raw/OMORI_cleaner/OMORI_cleaner.mid'

RAW_AUDIO_PATH = 'data/raw/busoni_sonata/Busoni_sonata_no2_op_8-BV_61_Scherzo.mp3'
PRED_MIDI_PATH = 'output/model_midi/Busoni_sonata_no2_op_8-BV_61_Scherzo_basic_pitch.mid'
GT_MIDI_PATH = 'data/raw/busoni_sonata/Busoni_sonata_no2_op_8-BV_61_Scherzo.mid'
TMP_PRED_MIDI_PATH = 'output/model_midi/tmp_pred.mid'

def objective_F1(trial: Trial) -> float:
    """
    Optimize the model parameters using Optuna.

    Args:
        trial (Trial): An Optuna trial object.

    Returns:
        float: The objective value to minimize.
    """
    # Define hyperparameters to optimize
    onset_th = trial.suggest_float("onset_threshold",0.1,0.6)
    frame_th = trial.suggest_float("frame_threshold", 0.1, 0.6)
    min_duration = trial.suggest_float("minimum_note_length", 0.01, 0.15)
 

    # Run the model with the suggested hyperparameters
    # midi_generator = model.midi_generator.audio_conversion(
    #     song='OMORI_cleaner', 
    #     audio_path='data/raw', 
    #     output_path='output/model_midi'
    # )
    
    #midi_generator.conversion_1()
    _, midi_data, _ = model.midi_generator.predict(
        audio_path_list=[RAW_AUDIO_PATH],
        onset_threshold=onset_th,
        frame_threshold=frame_th,
        minimum_note_length=min_duration,
        save_midi=True,
        sonify_midi=False,
        save_model_outputs=False,
        save_notes=False,
        model_or_model_path=model.midi_generator.ICASSP_2022_MODEL_PATH
    )
    midi_data.write(TMP_PRED_MIDI_PATH)
    # Evaluate the generated MIDI file
    evaluation_result = evaluation.evaluate_midi(
        midi_path=TMP_PRED_MIDI_PATH,
        midi_ground_truth_path=GT_MIDI_PATH
    )
    return evaluation_result['f1_score']

def optimize_model():
    """
    Optimize the model parameters using Optuna and print the best parameters and F1 score.
    """
    sampler = TPESampler(seed=42)
    study = optuna.create_study(direction="maximize", sampler=sampler)
    study.optimize(objective_F1, n_trials=50)

    print("Best hyperparameters:", study.best_params)
    print("Best F1 score:", study.best_value)

if __name__ == "__main__":

    optimize_model()
    # Run the model with the best hyperparameters
    # midi_generator = model.midi_generator.audio_conversion(
    #     song='OMORI_cleaner', 
    #     audio_path='data/raw', 
    #     output_path='output/model_midi'
    # )
    
    #midi_generator.conversion_1()