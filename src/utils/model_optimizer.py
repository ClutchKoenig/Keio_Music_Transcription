import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import optuna
from optuna import Trial
from optuna.samplers import TPESampler  
#import model.midi_generator
import evaluation
import midi_loading

from basic_pitch.inference import predict, predict_and_save, Model
from basic_pitch import ICASSP_2022_MODEL_PATH

# RAW_AUDIO_PATH = 'data/raw/OMORI_cleaner/OMORI_cleaner.mp3'
# PRED_MIDI_PATH = 'output/model_midi/OMORI_cleaner.mid'
# GT_MIDI_PATH = 'data/raw/OMORI_cleaner/OMORI_cleaner.mid'

RAW_AUDIO_PATH = 'data/raw/busoni_sonata/Busoni_sonata_no2_op_8-BV_61_Scherzo.mp3'
PRED_MIDI_PATH = 'output/model_midi/Busoni_sonata_no2_op_8-BV_61_Scherzo_basic_pitch.mid'
GT_MIDI_PATH = 'data/raw/busoni_sonata/Busoni_sonata_no2_op_8-BV_61_Scherzo.mid'
TMP_PRED_MIDI_PATH = 'output/model_midi/tmp_pred.mid'

def objective_F1(trial: Trial,hyperparameter:dict ,search_space: dict) -> float:
    """
    Optimize the model parameters using Optuna.

    Args:
        trial (Trial): An Optuna trial object.
        search_space (dict): A dictionary containing the hyperparameter search space.
        hyperparameter (dict): A dictionary containing the hyperparameters to optimize.
    Returns:
        float: The objective value to minimize.
    """
    if not os.path.exists('output/model_midi'):
        os.makedirs('output/model_midi')    
    # Check if the temporary MIDI file exists and remove it
    if os.path.exists(TMP_PRED_MIDI_PATH):
        os.remove(TMP_PRED_MIDI_PATH)   

    if search_space is None:
        print("Warning: Using default search space for hyperparameters.")
        # Default search space for hyperparameters
        search_space = {
            "onset_threshold": (0.1, 0.9),
            "frame_threshold": (0.1, 0.9),
            "minimum_note_length": (60, 160),  # in ms
            "tolerance": (0.01, 0.2),
            "minimum_overlap": (0.05, 0.8)
        }
    # Test for correct search space format
    print("Search space:", search_space)
    print("Hyperparameters to optimize:", hyperparameter)

    params = hyperparameter.copy()
    print(f"params before adding bounds: {params}")
    # Overwrite hyperparameters with trial suggestions if they exist in the search space
    for key, bounds in search_space.items():
        if( "onset_threshold" in key or 
           "frame_threshold" in key or 
           "tolerance" in key or 
           "minimum_overlap" in key):
            params[key] = trial.suggest_float(key, *bounds)
        else:
            # only integer hyperparameters is minimum_note_length 
            params[key] = trial.suggest_int(key, *bounds)
    print(f"params after adding bounds: {params}")
    # if 'onset_threshold' in search_space:
    #     onset_threshold = trial.suggest_float("onset_threshold", *search_space["onset_threshold"])
    # else:
    #     onset_threshold = hyperparameter["onset_threshold"]

    # if 'frame_threshold' in search_space:
    #     frame_threshold = trial.suggest_float("frame_threshold", *search_space["frame_threshold"])
    # else:
    #     frame_threshold = hyperparameter["frame_threshold"]

    # if 'minimum_note_length' in search_space:
    #     minimum_note_length = trial.suggest_int("minimum_note_length", *search_space["minimum_note_length"])
    # else:
    #     minimum_note_length = hyperparameter["minimum_note_length"]

    # if 'tolerance' in search_space:
    #     tolerance = trial.suggest_float("tolerance", *search_space["tolerance"])
    # else:
    #     tolerance = hyperparameter["tolerance"]
    # if 'minimum_overlap' in search_space:
    #     minimum_overlap = trial.suggest_float("minimum_overlap", *search_space["minimum_overlap"])
    # else:
    #     minimum_overlap = hyperparameter["minimum_overlap"]
    
    # Set hyperparameters from the trial

    # onset_threshold = trial.suggest_float("onset_threshold", search_space["onset_threshold"][0], search_space["onset_threshold"][1])
    # frame_threshold = trial.suggest_float("frame_threshold", search_space["frame_threshold"][0], search_space["frame_threshold"][1])
   
    # minimum_note_length = trial.suggest_int("minimum_note_length", search_space["minimum_note_length"][0], search_space["minimum_note_length"][1])
    #======================= old manual hyperparameter optimization =========================
    # # Define hyperparameters to optimize
    # onset_th = trial.suggest_float("onset_threshold",0.1,0.9)
    # frame_th = trial.suggest_float("frame_threshold", 0.1, 0.9)
    # min_duration = trial.suggest_int("minimum_note_length", 60, 160)  # 60-160 ms
 
    # tolerance = trial.suggest_float("tolerance", 0.01, 0.2)
    # min_overlap = trial.suggest_float("minimum_overlap", 0.05, 0.8) 
    #=========================================================================
    print(f"Trial {trial.number} hyperparameters:")
    onset_th = params['onset_threshold']
    frame_th = params['frame_threshold']
    min_duration = params['minimum_note_length']
    tolerance = params['tolerance']
    min_overlap = params['minimum_overlap']
    print(f"onset_threshold: {onset_th}, frame_threshold: {frame_th}, "
          f"minimum_note_length: {min_duration}, tolerance: {tolerance}, "
          f"minimum_overlap: {min_overlap}")
    
    # Predict the MIDI file using the model with the given hyperparameters
    _, midi_data, _ = predict(
        audio_path= RAW_AUDIO_PATH,
        onset_threshold=params['onset_threshold'],
        frame_threshold=params['frame_threshold'],
        minimum_note_length=params['minimum_note_length'],
        model_or_model_path=ICASSP_2022_MODEL_PATH
    )
    midi_data.write(TMP_PRED_MIDI_PATH)
    # Evaluate the generated MIDI file
    evaluation_result = evaluation.evaluate_midi(
        midi_path_pred=TMP_PRED_MIDI_PATH,
        midi_path_ground_truth=GT_MIDI_PATH,
        tolerance_note=params['tolerance'],
        overlap_note=params['minimum_overlap']    
    )
    # Clean up the temporary MIDI file
    #os.remove(TMP_PRED_MIDI_PATH)

    # Return the F1 score as the objective value
    print(f"F1={evaluation_result['f1_score']}")
    f1 = evaluation_result['f1_score']#['f1_score']

    # write the evaluation results for every trial to a file 
    number = 1
    f1_file_path = 'train_history/experiment/model_opti_params.txt'
    if not os.path.exists('train_history/experiment1'):
        os.makedirs('train_history/experiment1')

    with open(f1_file_path, 'a') as f:
        f.write(f"================ Trial{trial.number} ==================\n")
        f.write(f"F1 Score: {f1}\n")
        f.write(f"onset_threshold: {onset_th}\n")
        f.write(f"frame_threshold: {frame_th}\n")
        f.write(f"minimum_note_length: {min_duration}\n")
        f.write(f"tolerance: {tolerance}\n")
        f.write(f"minimum_overlap: {min_overlap}\n")
        f.write(f"=====================================================\n")
    print(f"Evaluation results written to {f1_file_path}")

    # Return the F1 score as the objective value    
    return f1

def optimize_model(hyperparameter_search_space=None, 
                   hyperparameters_to_optimize=None):
    """
    Optimize the model parameters using Optuna and print the best parameters and F1 score.
    """
    if hyperparameters_to_optimize is None:
        # Default hyperparameters to optimize
        hyperparameters_to_optimize = {
            "onset_threshold": 0.131,
            "frame_threshold": 0.33,
            "minimum_note_length": 61,  # in ms
            "tolerance": 0.189,
            "minimum_overlap": 0.6
        }
    if hyperparameter_search_space is None:
        # Default search space if not provided
        hyperparameter_search_space = {
            "onset_threshold": (0.15, 0.2),
            "frame_threshold": (0.3, 0.35),
            "minimum_note_length": (55, 70),  # in ms
            "tolerance": (0.2, 0.25),
            "minimum_overlap": (0.3, 0.5)
        }

    sampler = TPESampler(seed=42)
    study = optuna.create_study(direction="maximize", sampler=sampler)
    # study.optimize(objective_F1(lambda trial: objective_F1(trial, 
    #                                                        hyperparameter=hyperparameters_to_optimize, 
    #                                                        hyperparameter_search_space=hyperparameter_search_space)), 
    #                                                        n_trials=20)
    study.optimize(lambda trial: objective_F1(trial, hyperparameters_to_optimize, hyperparameter_search_space), n_trials=50)
    print("Best hyperparameters:", study.best_params)
    print("Best F1 score:", study.best_value)

if __name__ == "__main__":

    single_model_run = False  # Set to True for a single model run with fixed hyperparameters
    if single_model_run:
        print("Running single model run with fixed hyperparameters...")
        # Define fixed hyperparameters
        onset_th = 0.131
        frame_th = 0.33
        min_duration = 61  # 80 ms
        tolerance = 0.189
        min_overlap = 0.6

        _, midi_data, _ = predict(
            audio_path= RAW_AUDIO_PATH,
            onset_threshold=onset_th,
            frame_threshold=frame_th,
            minimum_note_length=min_duration,
            model_or_model_path=ICASSP_2022_MODEL_PATH,
            #melodia_trick=False
        )
        midi_data.write(TMP_PRED_MIDI_PATH)
        # Evaluate the generated MIDI file
        evaluation_result = evaluation.evaluate_midi(
            midi_path_pred=TMP_PRED_MIDI_PATH,
            midi_path_ground_truth=GT_MIDI_PATH,
            tolerance_note=tolerance,
            overlap_note=min_overlap
        )
        # Clean up the temporary MIDI file
        #os.remove(TMP_PRED_MIDI_PATH)

        # Return the F1 score as the objective value
        print(f"evaluation_results={evaluation_result}")
        print(f"F1={evaluation_result['f1_score']}")
        f1 = evaluation_result['f1_score']
        print("Best hyperparameters: (fixed)")
        print(f"onset_threshold: {onset_th}, frame_threshold: {frame_th}, "
            f"minimum_note_length: {min_duration}, tolerance: {tolerance}, "
            f"minimum_overlap: {min_overlap}")
    else:

        print("Starting model optimization...")

        hy_search_space = {
            "onset_threshold": (0.1, 0.175),
            #"frame_threshold": (0.3, 0.35),
            "minimum_note_length": (55, 70),  # in ms
            #"tolerance": (0.2, 0.25),
            #"minimum_overlap": (0.3, 0.5)
        }
        hy_to_optimize = {
            #"onset_threshold": 0.131,
            "frame_threshold": 0.3365,
            #"minimum_note_length": 61,  # in ms
            "tolerance": 0.189,
            "minimum_overlap": 0.5
        }


        # Optimize the model parameters
        optimize_model(hyperparameter_search_space=hy_search_space, 
                       hyperparameters_to_optimize=hy_to_optimize)  
    
    #midi_generator.conversion_1()