"""Inspectable linear structural finite elements. All in-memory quantities use SI."""

from .identification import IdentificationConfig, IdentificationResult, Observation, fit_cantilever
from .model import Model, ModelError, model_from_dict, model_to_dict
from .solver import AssemblyTrace, SolveOptions, SolveResult, assemble, solve_linear

__version__ = "0.2.0"
__all__ = [
    "Model",
    "ModelError",
    "AssemblyTrace",
    "SolveResult",
    "assemble",
    "solve_linear",
    "model_from_dict",
    "model_to_dict",
    "SolveOptions",
    "IdentificationConfig",
    "IdentificationResult",
    "Observation",
    "fit_cantilever",
]
