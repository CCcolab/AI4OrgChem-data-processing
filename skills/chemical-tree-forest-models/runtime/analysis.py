"""Bounded decision tree/random forest training; no automatic selection."""
from .ml_support import supervised


def analyze(parameters, data, output_dir):
    return supervised(parameters, data, output_dir,
                      allowed={'tree_regression', 'forest_regression', 'forest_classification'})
