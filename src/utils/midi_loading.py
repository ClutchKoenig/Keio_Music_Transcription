import pretty_midi 



def load_midi(midi_path:str) -> pretty_midi.PrettyMIDI:
    """
    Load a MIDI file and return a PrettyMIDI object.

    Args:
        midi_path (str): Path to the MIDI file.

    Returns:
        pretty_midi.PrettyMIDI: A PrettyMIDI object representing the MIDI file.
    """
    try:
        midi_data = pretty_midi.PrettyMIDI(midi_path)
        return midi_data
    except Exception as e:
        raise ValueError(f"Error loading MIDI file: {e}")
def get_midi_instrument_names(midi_data: pretty_midi.PrettyMIDI) -> list[str]:
    """
    Get the names of instruments in a MIDI file.

    Args:
        midi_data (pretty_midi.PrettyMIDI): A PrettyMIDI object representing the MIDI file.

    Returns:
        list[str]: A list of instrument names.
    """
    return [instrument.name for instrument in midi_data.instruments if instrument.is_drum is False]

