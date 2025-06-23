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

def evaluate_midi(midi_path: str, ground_truth: list[str]) -> dict:
    """
    Evaluate a MIDI file against ground truth data.

    Args:
        midi_path (str): Path to the MIDI file.
        ground_truth (list[str]): List of expected instrument names.

    Returns:
        dict: A dictionary containing evaluation metrics.
    """
    try:
        midi_data = ml.load_midi(midi_path)
        predicted_instruments = ml.get_midi_instrument_names(midi_data)

        true_positives = len(set(predicted_instruments) & set(ground_truth))
        false_positives = len(set(predicted_instruments) - set(ground_truth))
        false_negatives = len(set(ground_truth) - set(predicted_instruments))

        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
        f1 = f1_score(precision, recall)

        return {
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "predicted_instruments": predicted_instruments,
            "ground_truth": ground_truth
        }
    except Exception as e:
        raise ValueError(f"Error evaluating MIDI file: {e}")