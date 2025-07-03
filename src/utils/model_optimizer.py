import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import optuna
from optuna import Trial
from optuna.samplers import TPESampler  
from optuna import visualization as vis
#import model.midi_generator
import evaluation
import midi_loading

from basic_pitch.inference import predict, predict_and_save, Model
from basic_pitch import ICASSP_2022_MODEL_PATH
from utils.split import splt
# RAW_AUDIO_PATH = 'data/raw/OMORI_cleaner/OMORI_cleaner.mp3'
# PRED_MIDI_PATH = 'output/model_midi/OMORI_cleaner.mid'
# GT_MIDI_PATH = 'data/raw/OMORI_cleaner/OMORI_cleaner.mid'

RAW_AUDIO_PATH = 'data/raw/busoni_sonata/Busoni_sonata_no2_op_8-BV_61_Scherzo.mp3'
PRED_MIDI_PATH = 'output/model_midi/Busoni_sonata_no2_op_8-BV_61_Scherzo_basic_pitch.mid'
GT_MIDI_PATH = 'data/raw/busoni_sonata/Busoni_sonata_no2_op_8-BV_61_Scherzo.mid'
TMP_PRED_MIDI_PATH = 'output/model_midi/tmp_pred.mid'

def plot_callback(study, trial):
    vis.plot_optimization_history(study).show()

def objective_F1(trial: Trial,hyperparameter:dict ,search_space: dict, experiment_name: str) -> float:
    """
    Optimize the model parameters using Optuna.

    Args:
        trial (Trial): An Optuna trial object.
        search_space (dict): A dictionary containing the hyperparameter search space.
        hyperparameter (dict): A dictionary containing the hyperparameters to optimize.
    Returns:
        float: The objective value to minimize.
    """
    # get experiment number from experiment_name
    # e.g. 'experiment1' -> 1
    if 'experiment' in experiment_name:
        try:
            exp_number = int(experiment_name.split('experiment')[1])
        except ValueError:
            print("Invalid experiment name format. Using default experiment number 9.")
            exp_number = 'Test'
    
    #number = 9  # Set the experiment number
    print(f"\n\n========================= Running Trial {trial.number} with experiment number {exp_number} ========================")

    if not os.path.exists('output/model_midi'):
        os.makedirs('output/model_midi')    
    # Check if the temp MIDI file exists, if yes rename it with number of current Trail attached and move it to 'output/model_midi/experiment{number}/....mid'
    if os.path.exists(TMP_PRED_MIDI_PATH):
        # Create the directory if it does not exist
        if not os.path.exists(f'output/model_midi/experiment{exp_number}'):
            os.makedirs(f'output/model_midi/experiment{exp_number}')
        # Rename the temporary MIDI file with the trial number
        # first trial tmp data belongs to previous experiment
        # therefore delete
        if trial.number==0:
            os.remove(TMP_PRED_MIDI_PATH)
        elif trial.number > 0:
            new_midi_path = f'output/model_midi/experiment{exp_number}/tmp_pred_{trial.number-1}.mid'
            os.rename(TMP_PRED_MIDI_PATH, new_midi_path)
            print(f"Renamed temporary MIDI file to {new_midi_path}")
    else:
        print(f"Temporary MIDI file {TMP_PRED_MIDI_PATH} does not exist. Creating a new one.")

        # remove in case 
        #os.remove(TMP_PRED_MIDI_PATH)   

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

    params = hyperparameter.copy()

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
    #======================= old manual hyperparameter optimization =========================
    # # Define hyperparameters to optimize
    # onset_th = trial.suggest_float("onset_threshold",0.1,0.9)
    # frame_th = trial.suggest_float("frame_threshold", 0.1, 0.9)
    # min_duration = trial.suggest_int("minimum_note_length", 60, 160)  # 60-160 ms
 
    # tolerance = trial.suggest_float("tolerance", 0.01, 0.2)
    # min_overlap = trial.suggest_float("minimum_overlap", 0.05, 0.8) 
    #=========================================================================
    # Test for correct search space format
    print("Search space:", search_space)
    print("Hyperparameters to optimize:", search_space.keys())
    # Print the hyperparameters for the current trial with colored output
    print("\033[1;34m" + f"Trial {trial.number} hyperparameters:" + "\033[0m")
    

    onset_th = params['onset_threshold']
    frame_th = params['frame_threshold']
    min_duration = params['minimum_note_length']
    tolerance = params['tolerance']
    min_overlap = params['minimum_overlap']

    # Print the hyperparameters for the current trial with colored output
    print(
        f"\033[31mOnset Threshold:\033[0m \033[1m{onset_th}\033[0m, "
        f"\033[34mFrame Threshold:\033[0m \033[1m{frame_th}\033[0m, "
        f"\033[32mMinimum Note Length:\033[0m \033[1m{min_duration}\033[0m, "
        f"\033[35mTolerance:\033[0m \033[1m{tolerance}\033[0m, "
        f"\033[36mMinimum Overlap:\033[0m \033[1m{min_overlap}\033[0m\n"
    )    
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
    #number = 5
    if not os.path.exists(f'train_history/experiment{exp_number}'):
        os.makedirs(f'train_history/experiment{exp_number}')

    f1_file_path = f'train_history/experiment{exp_number}/model_opti_params.txt'
    with open(f1_file_path, 'a') as f:
        f.write(f"================ Trial{trial.number} ==================\n")
        f.write(f"search_space: {search_space}\n")
        f.write(f"F1 Score: {f1}, Precision: {evaluation_result['precision']}, Recall: {evaluation_result['recall']}\n")
        f.write(f"True Positives: {evaluation_result['true_positives']}, false Positives: {evaluation_result['false_positives']}, false Negatives: {evaluation_result['false_negatives']}\n")
        f.write(f"onset_threshold: {onset_th}\n")
        f.write(f"frame_threshold: {frame_th}\n")
        f.write(f"minimum_note_length: {min_duration}\n")
        f.write(f"tolerance: {tolerance}\n")
        f.write(f"minimum_overlap: {min_overlap}\n")
        f.write(f"=====================================================\n")
    print(f"Evaluation results written to {f1_file_path}")
    # End of Trial
    print(f"========================= End of Running Trial {trial.number} with experiment number {exp_number} ========================")
    # Return the F1 score as the objective value    
    return f1

def optimize_model(hyperparameter_search_space=None, 
                   hyperparameters_to_optimize=None,
                   experiment_name="Experiment_test"):
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
    study = optuna.create_study(direction="maximize", sampler=sampler, storage="sqlite:///example.db",
                               study_name=experiment_name, load_if_exists=True)
    # study.optimize(objective_F1(lambda trial: objective_F1(trial, 
    #                                                        hyperparameter=hyperparameters_to_optimize, 
    #                                                        hyperparameter_search_space=hyperparameter_search_space)), 
    #                                                        n_trials=20)
    study.optimize(lambda trial: objective_F1(trial, hyperparameters_to_optimize, hyperparameter_search_space, experiment_name=experiment_name), n_trials=50)
    print("Best hyperparameters:", study.best_params)
    print("Best F1 score:", study.best_value)

if __name__ == "__main__":

    test=False  # Set to True for testing the model with fixed hyperparameters without optimization
    single_model_run = False  # Set to True for a single model run with fixed hyperparameters
    if single_model_run and test== False:
        print("Running single model run with fixed hyperparameters...")
        # Define fixed hyperparameters
        onset_th = 0.6
        frame_th = 0.6
        min_duration = 90  # 80 ms
        tolerance = 1
        min_overlap = 0.01
        # shows a good starting place for hyperparameter optimization
        _, midi_data, _ = predict(
            audio_path= RAW_AUDIO_PATH,
            onset_threshold=onset_th,
            frame_threshold=frame_th,
            minimum_note_length=min_duration,
            model_or_model_path=ICASSP_2022_MODEL_PATH,
            #midi_tempo = 180

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
    elif test==False:
        # If test is False, run the model optimization
        print("\033[1;32mStarting model optimization...\033[0m")  # Green bold text


        # Change Raw Audio Path to split audio lines from spleeter
        #print("Starting model optimization...")
        # Define the hyperparameter search space and hyperparameters to optimize
        #=======================
        hy_search_space = {
            "onset_threshold": (0.6, 0.8),
            "frame_threshold": (0.3, 0.6),
            "minimum_note_length": (65, 75),  # in ms
            #"tolerance": (0.2, 0.25),
        }
        hy_to_optimize = {
            #"onset_threshold": 0.131,
            #"frame_threshold": 0.3365,
            #"minimum_note_length": 40,  # in ms
            "tolerance": 1,
            "minimum_overlap": 0.1
        }
        #=======================

        # Optimize the model parameters
        # Experiment name can be used to differentiate between different runs
        # e.g. "experiment1", "experiment2", etc.
        experiment_name = "experiment13"
        optimize_model(hyperparameter_search_space=hy_search_space, 
                       hyperparameters_to_optimize=hy_to_optimize,
                       experiment_name= experiment_name)  
    
    else:
        RAW_AUDIO_PATH= 'data/raw/OMORI_cleaner/OMORI_cleaner.mp3'
        print("Running test with fixed hyperparameters...")
        # Define fixed hyperparameters for testing
        hyperparameter = {
            "onset_threshold": 0.5015,
            "frame_threshold": 0.5144,
            "minimum_note_length": 67,  # in ms
            "tolerance": 1,
            "minimum_overlap": 0.1
        }
        # Predict the MIDI file using the model with the given hyperparameters
        _, midi_data, _ = predict(
            audio_path= RAW_AUDIO_PATH,
            onset_threshold=hyperparameter['onset_threshold'],
            frame_threshold=hyperparameter['frame_threshold'],
            minimum_note_length=hyperparameter['minimum_note_length'],
            model_or_model_path=ICASSP_2022_MODEL_PATH
        )
        TMP_PRED_MIDI_PATH = 'output/model_midi/OMORI.mid'
        midi_data.write(TMP_PRED_MIDI_PATH)
        # Run the objective function with the fixed hyperparameters
        # f1_score = objective_F1(None, hyperparameter, None)
        # print(f"Test F1 score: {f1_score}")
    #midi_generator.conversion_1()