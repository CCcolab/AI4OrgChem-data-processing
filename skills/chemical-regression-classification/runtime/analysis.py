"""Local Ridge or binary logistic baseline with explicit holdout."""
from .ml_support import supervised


def analyze(parameters, data, output_dir):
    return supervised(parameters, data, output_dir, allowed={'ridge', 'logistic'})
