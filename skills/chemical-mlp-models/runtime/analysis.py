"""Tiny real MLP fitting with train-only scaling and convergence disclosure."""
from .ml_support import supervised


def analyze(parameters, data, output_dir):
    return supervised(parameters, data, output_dir, allowed={'mlp_regression', 'mlp_classification'})
