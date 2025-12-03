"""Оркестрация пайплайна проверки."""

from __future__ import annotations

import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

from backend.grading.backends.base import Backend
from backend.grading.io_utils import load_samples, save_results_jsonl
from backend.grading.types import GradingResult, Sample


def _clamp_confidence(value: float) -> float:
    if math.isnan(value):
        return 0.0
    return max(0.0, min(1.0, float(value)))


def _normalize_result(
    raw_result: GradingResult,
    backend: Backend,
    sample: Sample,
    experiment_name: str,
    timestamp: str,
) -> GradingResult:
    result = {**raw_result}
    # Гарантируем наличие базовых полей и привязываем техническую метку эксперимента.
    result.setdefault("student_id", sample["student_id"])
    result.setdefault("task_id", sample["task_id"])
    result.setdefault("true_score", sample["true_score"])
    result.setdefault("max_score", sample["max_score"])
    result.setdefault("backend_name", backend.name)
    result.setdefault("model_name", getattr(backend, "model_name", backend.name))
    result.setdefault("timestamp", timestamp)
    result["experiment_name"] = experiment_name
    result["confidence"] = _clamp_confidence(result.get("confidence", 0.0))
    return result  # type: ignore[return-value]


def grade_dataset(samples: Sequence[Sample], backend: Backend, experiment_name: str | None = None) -> List[GradingResult]:
    experiment_name = experiment_name or f"{backend.name}_{datetime.now(tz=timezone.utc).strftime('%Y%m%dT%H%M%S')}"
    timestamp = datetime.now(tz=timezone.utc).isoformat()
    results: List[GradingResult] = []

    for sample in samples:
        raw_result = backend.grade(sample)
        results.append(_normalize_result(raw_result, backend, sample, experiment_name, timestamp))

    return results


def run_task_directory(
    task_dir: Path,
    backend: Backend,
    experiment_name: str | None = None,
    results_dir: Path | None = None,
    labels_filename: str = "labels.csv",
    metadata: dict | None = None,
) -> Tuple[List[GradingResult], Path]:
    samples = load_samples(task_dir, labels_filename=labels_filename)
    results = grade_dataset(samples, backend, experiment_name=experiment_name)

    experiment_name = results[0]["experiment_name"] if results else experiment_name or "empty_experiment"
    output_dir = results_dir or Path("results")
    output_path = (output_dir / f"{experiment_name}.jsonl").resolve()

    save_results_jsonl(results, output_path, metadata=metadata or {})
    return results, output_path


def grade_single_sample(sample: Sample, backend: Backend, experiment_name: str | None = None) -> GradingResult:
    results = grade_dataset([sample], backend, experiment_name=experiment_name)
    return results[0]
