from jsons import set_serializer, dump, set_validator, set_deserializer
from os import mkdir, path
from typing import List

from .ballot_box import CiphertextBallot
from .decryption_mediator import PlaintextTally
from .election import CiphertextElectionContext, ElectionConstants, ElectionDescription
from .group import ElementModP, ElementModQ, int_to_p_unchecked, int_to_q_unchecked
from .key_ceremony import CoefficientValidationSet
from .tally import CiphertextTally

RESULTS_DIR = "results"
COEFFICIENTS_DIR = path.join(RESULTS_DIR, "coefficients")
BALLOTS_DIR = path.join(RESULTS_DIR, "encrypted_ballots")
SPOILED_DIR = path.join(RESULTS_DIR, "spoiled_ballots")

DESCRIPTION_FILE_NAME = "description"
CONTEXT_FILE_NAME = "context"
CONSTANTS_FILE_NAME = "constants"
ENCRYPTED_TALLY_FILE_NAME = "encrypted_tally"
TALLY_FILE_NAME = "tally"

COEFFICIENT_PREFIX = "coefficient_validation_set_"
BALLOT_PREFIX = "ballot_"


def publish(
    description: ElectionDescription,
    context: CiphertextElectionContext,
    constants: ElectionConstants,
    ciphertext_ballots: List[CiphertextBallot],
    ciphertext_tally: CiphertextTally,
    plaintext_tally: PlaintextTally,
    coefficient_validation_sets: List[CoefficientValidationSet] = None,
    results_directory: str = RESULTS_DIR,
) -> None:
    """Publishes the election record as json"""

    set_serializers()

    make_directory(results_directory)
    description.to_json_file(DESCRIPTION_FILE_NAME, results_directory)
    context.to_json_file(CONTEXT_FILE_NAME, results_directory)
    constants.to_json_file(CONSTANTS_FILE_NAME, results_directory)

    make_directory(COEFFICIENTS_DIR)
    if coefficient_validation_sets is not None:
        for coefficient_validation_set in coefficient_validation_sets:
            set_name = COEFFICIENT_PREFIX + coefficient_validation_set.owner_id
            coefficient_validation_set.to_json_file(set_name, COEFFICIENTS_DIR)

    make_directory(BALLOTS_DIR)
    for ballot in ciphertext_ballots:
        ballot_name = BALLOT_PREFIX + ballot.object_id
        ballot.to_json_file(ballot_name, BALLOTS_DIR)

    make_directory(SPOILED_DIR)
    for ballot in ciphertext_tally.spoiled_ballots.values():
        ballot_name = BALLOT_PREFIX + ballot.object_id
        ballot.to_json_file(ballot_name, SPOILED_DIR)

    ciphertext_tally.to_json_file(ENCRYPTED_TALLY_FILE_NAME, results_directory)
    plaintext_tally.to_json_file(TALLY_FILE_NAME, results_directory)


def make_directory(directory_path: str) -> None:
    """Create a directory only if it does not exist"""
    if not path.exists(directory_path):
        mkdir(directory_path)


def set_serializers() -> None:
    """Set serializers for jsons to use to cast specific classes"""
    set_serializer(lambda p, **_: str(p), ElementModP)
    set_serializer(lambda q, **_: str(q), ElementModQ)
    set_serializer(lambda tally, **_: dump(tally.cast), CiphertextTally)
    set_serializer(lambda tally, **_: dump(tally.contests), PlaintextTally)


def set_deserializers() -> None:
    """Set deserializers and validators for json to use to cast specific classes"""
    set_deserializer(
        lambda p_as_int, cls, **_: int_to_p_unchecked(p_as_int), ElementModP
    )
    set_validator(lambda p: p.is_in_bounds(), ElementModP)

    set_deserializer(
        lambda q_as_int, cls, **_: int_to_q_unchecked(q_as_int), ElementModQ
    )
    set_validator(lambda q: q.is_in_bounds(), ElementModQ)
