import logging
from collections import defaultdict

import music21
import numpy as np

logger = logging.getLogger(__name__)


def calculate_chord_entropy(midi_file: str) -> float:
    """
    Calculate the chord entropy of a MIDI file. Entropy score is a measure of the
    predictability of the chord progression. A higher entropy score indicates a more
    unpredictable chord progression.

    - Maximum Entropy = log₂(n)
    - Minimum Entropy = 0

    Args:
        midi_file: str, path to the MIDI file
    Returns:
        float, the chord entropy of the MIDI file

    """
    score = music21.converter.parse(midi_file)
    chords = score.chordify()

    logger.info(f"Chordified score: {chords}")

    # Extract chord progressions
    chord_sequence: list[list[str]] = []
    for chord in chords.flat.notes:
        if getattr(chord, "isChord", False):
            chord_sequence.append(chord.pitchNames)
    logger.info(f"Chord sequence length: {len(chord_sequence)}")

    # Calculate transition entropy - count the no. of times each transition occurs
    transitions: dict[str, int] = defaultdict(int)
    for i in range(len(chord_sequence) - 1):
        logger.info(f"Transition: {chord_sequence[i]} -> {chord_sequence[i+1]}")
        transitions[str((chord_sequence[i], chord_sequence[i + 1]))] += 1
    logger.info(f"Transitions length: {len(transitions)}")
    if transitions:
        most_common = max(transitions, key=lambda k: transitions[k])
        logger.info(
            "Most common transition: %s, with count %s",
            most_common,
            transitions[most_common],
        )

    # Shannon entropy calculation h(x) = -log( p(x) )
    # For each transition, calculate the probability of the transition
    # and then calculate the entropy
    total = sum(transitions.values())
    logger.info(f"Total: {total}")
    if total == 0:
        logger.warning("No transitions found, returning entropy 0.0")
        return 0.0
    entropy = -sum(
        (count / total) * np.log2(count / total) for count in transitions.values()
    )
    logger.info(f"Entropy: {entropy}")
    return float(entropy)


def calculate_chord_entropy_from_global_transition_matrix(
    midi_file: str,
    global_transition_matrix: dict[str, float],
    normalized: bool = False,
) -> float:
    """
    Calculate the chord entropy of a MIDI file using a pre-calculated global
    transition matrix.

    This function uses the global transition probabilities from a dataset to
    calculate the entropy of a new MIDI file, providing a measure of harmonic
    complexity relative to the training dataset.

    Args:
        midi_file: str, path to the MIDI file
        global_transition_matrix: dict, pre-calculated transition matrix where:
            - keys are transition strings like "('C', 'G')"
            - values are probabilities (should sum to 1.0)
        normalized: bool, if True returns normalized entropy (0-1),
            if False returns raw entropy

    Returns:
        float, the chord entropy of the MIDI file based on global transition
        probabilities
        - If normalized=True: score between 0 and 1 (0=predictable, 1=unpredictable)
        - If normalized=False: raw entropy value
    """
    score = music21.converter.parse(midi_file)
    chords = score.chordify()

    # Extract chord sequence
    chord_sequence: list[list[str]] = [
        chord.pitchNames
        for chord in chords.flat.notes
        if getattr(chord, "isChord", False)
    ]
    logger.info(f"Chord sequence length: {len(chord_sequence)}")

    if len(chord_sequence) < 2:
        logger.warning("Chord sequence too short for entropy calculation")
        return 0.0

    # Calculate transitions in the new file
    transitions: dict[str, int] = defaultdict(int)
    for i in range(len(chord_sequence) - 1):
        transition_key = str((chord_sequence[i], chord_sequence[i + 1]))
        transitions[transition_key] += 1

    logger.info(f"Unique transitions in file: {len(transitions)}")

    # Calculate entropy using global transition probabilities
    total_transitions = sum(transitions.values())
    if total_transitions == 0:
        logger.warning("No transitions found, returning entropy 0.0")
        return 0.0
    entropy = 0.0

    for transition_key, count in transitions.items():
        if transition_key in global_transition_matrix:
            # Use global probability for this transition
            global_probability = global_transition_matrix[transition_key]
            if global_probability > 0:  # Avoid log(0)
                # Weight by how often this transition occurs in the new file
                local_probability = count / total_transitions
                entropy -= local_probability * np.log2(global_probability)
        else:
            # Handle unseen transitions - assign very low probability
            logger.debug(f"Unseen transition: {transition_key}")
            local_probability = count / total_transitions
            # Use a very small probability for unseen transitions
            unseen_probability = 1e-10
            entropy -= local_probability * np.log2(unseen_probability)

    # Normalize if requested
    if normalized:
        # Calculate maximum possible entropy for this file
        unique_transitions = set(transitions.keys())
        max_entropy = (
            np.log2(len(unique_transitions)) if len(unique_transitions) > 0 else 0
        )

        # Normalize to 0-1 scale
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
        logger.info(f"Normalized entropy: {normalized_entropy}")
        return float(normalized_entropy)
    else:
        logger.info(f"Entropy (using global matrix): {entropy}")
        return float(entropy)


def build_global_transition_matrix(midi_files: list[str]) -> dict[str, float]:
    """
    Build a global transition matrix from a dataset of MIDI files.

    This function analyzes multiple MIDI files to create a probability distribution
    of chord transitions that can be used for entropy calculations on new files.

    Args:
        midi_files: list of str, paths to MIDI files in the dataset

    Returns:
        dict, global transition matrix where:
            - keys are transition strings like "('C', 'G')"
            - values are probabilities (sum to 1.0)
    """
    global_transitions: dict[str, int] = defaultdict(int)
    total_transitions: int = 0

    logger.info("Building global transition matrix from %d files", len(midi_files))

    for midi_file in midi_files:
        try:
            score = music21.converter.parse(midi_file)
            chords = score.chordify()
            chord_sequence: list[list[str]] = [
                chord.pitchNames
                for chord in chords.flat.notes
                if getattr(chord, "isChord", False)
            ]

            # Count transitions in this file
            for i in range(len(chord_sequence) - 1):
                transition_key = str((chord_sequence[i], chord_sequence[i + 1]))
                global_transitions[transition_key] += 1
                total_transitions += 1

        except Exception as e:
            logger.warning("Failed to process %s: %s", midi_file, e)
            continue

    # Convert counts to probabilities
    global_transition_matrix: dict[str, float] = {}
    if total_transitions == 0:
        logger.warning("No transitions found in dataset, returning empty matrix")
        return global_transition_matrix
    for transition, count in global_transitions.items():
        global_transition_matrix[transition] = count / total_transitions

    logger.info(
        "Global transition matrix built with %d unique transitions",
        len(global_transition_matrix),
    )
    logger.info("Total transitions analyzed: %d", total_transitions)

    return global_transition_matrix


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("Calculating chord entropy...")
    # calculate_chord_entropy("pop909_021/021.mid")

    global_transition_matrix = build_global_transition_matrix(["pop909_021/021.mid"])
    calculate_chord_entropy_from_global_transition_matrix(
        "pop909_021/021.mid", global_transition_matrix
    )
    calculate_chord_entropy_from_global_transition_matrix(
        "pop909_021/021.mid", global_transition_matrix, normalized=True
    )
