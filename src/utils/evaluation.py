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
def f1_score_with_overlap(midi_path_pred: str, midi_ground_truth_path: str, tolerance:float=0.05, min_overlap:float=0.5) -> float:
    """
    Calculate the F1 score with overlap tolerance for MIDI files.

    Args:
        midi_path_pred (str): Path to the predicted MIDI file.
        midi_ground_truth_path (str): Path to the ground truth MIDI file.
        tolerance (float): Tolerance for overlap in seconds.
        min_overlap (float): Minimum overlap required to consider a note as true positive.

    Returns:
        float: The F1 score with overlap tolerance.
    """
    try:
        predicted_data = ml.load_midi(midi_path_pred)
        ground_truth_data = ml.load_midi(midi_ground_truth_path)

        predicted_notes = ml.extract_notes(predicted_data)
        ground_truth_notes = ml.extract_notes(ground_truth_data)

        if not predicted_notes or not ground_truth_notes:
            raise ValueError("No notes found in one of the MIDI files.")

        true_positives = 0
        false_positives = 0
        false_negatives = 0

        for pred_note in predicted_notes:
            matched = False
            for gt_note in ground_truth_notes:
                if abs(pred_note.start - gt_note.start) <= tolerance and abs(pred_note.end - gt_note.end) <= tolerance:
                    overlap = min(pred_note.end, gt_note.end) - max(pred_note.start, gt_note.start)
                    if overlap >= min_overlap:
                        true_positives += 1
                        matched = True
                        break
            if not matched:
                false_positives += 1

        false_negatives = len(ground_truth_notes) - true_positives

        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
        f1 = f1_score(precision, recall)

        return f1
    except Exception as e:
        raise ValueError(f"Error calculating F1 score with overlap: {e}")  


def evaluate_midi(midi_path_pred: str, midi_ground_truth_path:str) -> dict:
    """
    Evaluate a MIDI file against ground truth data.

    Args:
        midi_path_pred (str): Path to the predicted MIDI file.
        midi_ground_truth_path (str): Path to the ground truth MIDI file.
    Returns:
        dict: A dictionary containing evaluation metrics.
    """
    try:
        midi_data = ml.load_midi(midi_path_pred)
        predicted_instruments = ml.get_midi_instrument_names(midi_data)
        notes = ml.extract_notes(midi_data)

        if not notes:
            raise ValueError("No notes found in the predicted MIDI file.")
        
        # Load ground truth MIDI file
        ground_truth_data = ml.load_midi(midi_ground_truth_path)
        notes = ml.extract_notes(ground_truth_data)

        if not notes:
            raise ValueError("No notes found in the ground truth MIDI file.")
        
        # Get ground truth instrument names
        midi_ground_truth_path = ml.get_midi_instrument_names(ground_truth_data)
        if not midi_ground_truth_path:
            raise ValueError("No instruments found in the ground truth MIDI file.")
        

        true_positives = len(set(predicted_instruments) & set(midi_ground_truth_path))
        false_positives = len(set(predicted_instruments) - set(midi_ground_truth_path))
        false_negatives = len(set(midi_ground_truth_path) - set(predicted_instruments))

        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
        f1 = f1_score(precision, recall)

        return {
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "predicted_midi": midi_path_pred,
            "ground_truth": midi_ground_truth_path

        }
    except Exception as e:
        raise ValueError(f"Error evaluating MIDI file: {e}")