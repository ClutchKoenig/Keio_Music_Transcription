import midi_loading as ml

def f1_score(precision: float, recall: float) -> float:
    """
    Calculate the F1 score given precision and recall.

    Args:
        precision (float): The precision value.
        recall (float): The recall value.

    Returns:
        float: The F1 score.
    """
    if precision + recall == 0:
        return 0.0
    return 2 * (precision * recall) / (precision + recall)

def f1_score_with_overlap(predicted_notes: dict, ground_truth_notes: dict, tolerance:float=3, min_overlap:float=0.25) -> dict:
    """    
        Calculate the F1 score with overlap tolerance for predicted and ground truth notes.
        This function compares predicted notes with ground truth notes, allowing for a specified tolerance in start and end times,
        and a minimum overlap duration to consider a note as a true positive.

        Default tolerance is set to 0.05 seconds and minimum overlap to 0.5 seconds.

        Args:

        predicted_notes (dict): Dictionary of predicted notes with keys 'pitch', 'start', 'end', and 'instrument'.
        ground_truth_notes (dict): Dictionary of ground truth notes with keys 'pitch', 'start', 'end', and 'instrument'.
        tolerance (float): Tolerance for overlap in seconds.        
        min_overlap (float): Minimum overlap required to consider a note as true positive. given as a percentage of the shorter note's duration.

    Returns:
        dict: A dictionary containing the F1 score, precision, and recall.
    """

    try:
        # Initialize counters for true positives, false positives, and false negatives
        true_positives = 0
        false_positives = 0
        false_negatives = 0
        # Iterate through predicted instruments
        # and match with ground truth instruments

        # Iterate through predicted notes and match with ground truth notes
        for pred_note in predicted_notes:
            # export to csv file

            matched = False
            for gt_note in ground_truth_notes:
                if (
                    pred_note['pitch'] == gt_note['pitch'] and
                    abs(pred_note['start'] - gt_note['start']) <= tolerance #and
                    #abs(pred_note['end'] - gt_note['end']) <= tolerance
                ):
                    # print("================================================")
                    # print(f"Matching Predicted Note: {pred_note}")
                    # print(f"Matching Ground Truth Note: {gt_note}")
                    # Check if the notes overlap
                    # If the start of the predicted note is before the end of the ground truth note
                    # and the end of the predicted note is after the start of the ground truth note
                    # This means the notes overlap
                    overlap = min(pred_note['end'], gt_note['end']) - max(pred_note['start'], gt_note['start'])
                    # print(f"Overlap: {overlap}")
                    # If the overlap is greater than or equal to the minimum required overlap   
                    # Calculate the minimum required overlap as a percentage of the shorter note's duration
                    min_note_duration = min(pred_note['end'] - pred_note['start'], gt_note['end'] - gt_note['start'])
                    required_overlap = min_note_duration * min_overlap
                    if overlap >= required_overlap:
                        true_positives += 1
                        matched = True
                        break
                    #true_positives += 1
                    #print(f"+1")
                    #matched = True
                    #break
            if not matched:
                false_positives += 1

        false_negatives = len(ground_truth_notes) - true_positives
        print(f"True Positives: {true_positives}, False Positives: {false_positives}, False Negatives: {false_negatives}")
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
        f1 = f1_score(precision, recall)
        if f1 is None:
            raise ValueError("F1 score could not be calculated.")
        
        return dict(
            f1_score=f1,
            precision=precision,
            recall=recall,
            false_negatives=false_negatives,
            false_positives=false_positives,
            true_positives=true_positives
        )
    
    except Exception as e:
        raise ValueError(f"Error calculating F1 score with overlap and instruments: {e}")


def evaluate_midi(midi_path_pred: str, midi_path_ground_truth: str, tolerance_note: float=0.1, overlap_note: float=0.1) -> dict:
    """
    Evaluate a MIDI file against ground truth data, considering instruments.

    Args:
        midi_path (str): Path to the predicted MIDI file.
        midi_ground_truth_path (str): Path to the ground truth MIDI file.
    Returns:
        dict: A dictionary containing evaluation metrics per instrument.
    """
    try:
        predicted_data = ml.load_midi(midi_path_pred)
        ground_truth_data = ml.load_midi(midi_path_ground_truth)
    except Exception as e:
        raise ValueError(f"Error loading MIDI files: {e}")
    try:
        predicted_notes = ml.extract_all_notes(predicted_data)
        ground_truth_notes = ml.extract_all_notes(ground_truth_data)
        #PAUSE = input("Press Enter to continue...")
        # Export notes to CSV files for further analysis
        print('===============================================')
        print('\nExporting CSVs....')
        ml.export_notes_to_csv(predicted_notes, "output/predicted_notes.csv")
        ml.export_notes_to_csv(ground_truth_notes, "output/ground_truth_notes.csv")
        #PAUSE = input("Press Enter to continue...")
        #print(predicted_notes)
        #print(ground_truth_notes)
        if not predicted_notes or not ground_truth_notes:
            raise ValueError("No notes found in one of the MIDI files.")
    except Exception as e:
        raise ValueError(f"Error extracting notes from MIDI files: {e}")      

    try:
        f1 = f1_score_with_overlap(predicted_notes, ground_truth_notes, tolerance=tolerance_note, min_overlap=overlap_note)

        return {
            "f1_score": f1['f1_score'],
            "predicted_midi": midi_path_pred,
            "ground_truth": midi_path_ground_truth,
            "precision": f1['precision'],
            "recall": f1['recall'],
            "false_negatives": f1['false_negatives'],
            "false_positives": f1['false_positives'],   
            "true_positives": f1['true_positives'],
        }
    except Exception as e:
        raise ValueError(f"Error calculating F1-Score: {e}")

if __name__ == "__main__":
    # Example usage
    midi_path_pred = "output/model_midi/tmp_pred.mid"
    midi_path_ground_truth = "data/raw/busoni_sonata/Busoni_sonata_no2_op_8-BV_61_Scherzo.mid"
    
    try:
        evaluation_result = evaluate_midi("output/model_midi/tmp_pred.mid", "data/raw/busoni_sonata/Busoni_sonata_no2_op_8-BV_61_Scherzo.mid")
        print("Evaluation Result:", evaluation_result)
    except ValueError as e:
        print(f"Error during evaluation: {e}")


# def evaluate_midi_per_instrument(midi_path_pred: str, midi_path_ground_truth: str) -> dict:
#     """
#     Evaluate a MIDI file against ground truth data, considering instruments.

#     Args:
#         midi_path (str): Path to the predicted MIDI file.
#         midi_ground_truth_path (str): Path to the ground truth MIDI file.
#     Returns:
#         dict: A dictionary containing evaluation metrics per instrument.
#     """
#     # THis function is not functional at all probably can be used at a later point for polyphonic music
    
#     try:
#         predicted_data = ml.load_midi(midi_path_pred)
#         ground_truth_data = ml.load_midi(midi_path_ground_truth)

#         predicted_notes = ml.extract_notes(predicted_data)
#         ground_truth_notes = ml.extract_notes(ground_truth_data)
    
#         if not predicted_notes or not ground_truth_notes:
#             raise ValueError("No notes found in one of the MIDI files.")

#         # predicted_instruments = list(ml.get_midi_instrument_names(predicted_data))
#         # ground_truth_instruments = list(ml.get_midi_instrument_names(ground_truth_data))

#         if not predicted_instruments or not ground_truth_instruments:
#             raise ValueError("No instruments found in one of the MIDI files.")
#         f1_scores = {}
#         # basic pitch can apparently not recognize instruments, so all predicted notes have to be 
#         # combared to all ground truth notes 
#         # Check if all predicted instruments are in ground truth instruments
#         print("Predicted Instruments:", predicted_instruments)
#         print("Ground Truth Instruments:", ground_truth_instruments)
#         for instrument in predicted_instruments:
#             if instrument not in ground_truth_instruments:
#                 raise ValueError(f"Instrument '{instrument}' in predicted MIDI not found in ground truth MIDI.")
#             else:
#                 print(f"Instrument '{instrument}' found in both predicted and ground truth MIDI files.")
#                 # Calculate F1 score with overlap and instrument matching
#                 instrument_pred_notes = predicted_notes[instrument]
#                 instrument_gt_notes = ground_truth_notes[instrument]
#                 f1 = f1_score_with_overlap(instrument_pred_notes, instrument_gt_notes)
#                 f1_scores[instrument] = f1
#         f1_mean = sum(f1_scores[:][f1_score]) / len(f1_scores)
#         f1_scores['mean'] = f1_mean
#     except Exception as e:
#         raise ValueError(f"Error loading MIDI files: {e}")
    
#     try:
#         # Calculate F1 score with overlap and instrument matching
#         f1 = f1_score_with_overlap(midi_path_pred, midi_path_ground_truth)

#         return {
#             "evaluation": f1_scores,
#             "f1_score": f1['mean'],
#             "predicted_instruments": ['predicted_instruments'],
#             "ground_truth_instruments": ['ground_truth_instruments'],
#             "predicted_midi": midi_path_pred,
#             "ground_truth": midi_path_ground_truth
#         }
    
#     except Exception as e:
#         raise ValueError(f"Error evaluating MIDI file: {e}")




# # Prototype for F1 score with overlap tolerance
# def f1_score_with_overlap(midi_path_pred: str, midi_ground_truth_path: str, tolerance:float=0.05, min_overlap:float=0.5) -> float:
#     """
#     Calculate the F1 score with overlap tolerance for MIDI files.

#     Args:
#         midi_path_pred (str): Path to the predicted MIDI file.
#         midi_ground_truth_path (str): Path to the ground truth MIDI file.
#         tolerance (float): Tolerance for overlap in seconds.
#         min_overlap (float): Minimum overlap required to consider a note as true positive.

#     Returns:
#         float: The F1 score with overlap tolerance.
#     """
#     try:
#         predicted_data = ml.load_midi(midi_path_pred)
#         ground_truth_data = ml.load_midi(midi_ground_truth_path)

#         predicted_notes = ml.extract_notes(predicted_data)
#         ground_truth_notes = ml.extract_notes(ground_truth_data)

#         if not predicted_notes or not ground_truth_notes:
#             raise ValueError("No notes found in one of the MIDI files.")

#         true_positives = 0
#         false_positives = 0
#         false_negatives = 0

#         for pred_note in predicted_notes:
#             matched = False
#             for gt_note in ground_truth_notes:
#                 if (
#                     pred_note['pitch'] == gt_note['pitch'] and
#                     abs(pred_note['start'] - gt_note['start']) <=tolerance and
#                     abs(pred_note['end'] - gt_note['end']) <= tolerance
#                 ):
#                     overlap = min(pred_note.end, gt_note.end) - max(pred_note.start, gt_note.start)
#                     if overlap >= min_overlap:
#                         true_positives += 1
#                         matched = True
#                         break
#             if not matched:
#                 false_positives += 1

#         false_negatives = len(ground_truth_notes) - true_positives

#         precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
#         recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
#         f1 = f1_score(precision, recall)

#         return f1
#     except Exception as e:
#         raise ValueError(f"Error calculating F1 score with overlap: {e}")  

# Prototype for F1 score with overlap tolerance and instrument matching