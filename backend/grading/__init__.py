"""Точка входа для инструментов проверки."""

from backend.grading.backends.dummy_backend import DummyBackend
from backend.grading.pipeline import grade_dataset, grade_single_sample, run_task_directory
from backend.grading.types import GradingBackend, GradingResult, ReliabilityBin, Sample

__all__ = [
    "DummyBackend",
    "GradingBackend",
    "GradingResult",
    "ReliabilityBin",
    "Sample",
    "grade_dataset",
    "grade_single_sample",
    "run_task_directory",
]
