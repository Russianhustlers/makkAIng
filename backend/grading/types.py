"""Типы и интерфейсы, используемые в пайплайне проверки."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, NotRequired, Protocol, TypedDict, runtime_checkable


class Sample(TypedDict):
    """Один рукописный ответ ученика с привязкой к условию и истинному баллу."""

    task_id: str
    student_id: str
    image_path: str
    statement_text: str
    rubric_text: str
    true_score: int
    max_score: int
    solution_text: NotRequired[str]
    meta: NotRequired[Dict[str, object]]


class GradingResult(TypedDict, total=False):
    """Ответ бэкенда/LLM по конкретному ученику и задаче."""

    student_id: str
    task_id: str
    true_score: int
    max_score: int
    pred_score: int
    confidence: float
    comment: str
    backend_name: str
    model_name: str
    raw_response: dict
    timestamp: str
    experiment_name: str


@runtime_checkable
class GradingBackend(Protocol):
    """Интерфейс бэкенда; реализация может быть заглушкой или реальной моделью."""

    name: str
    model_name: str

    def grade(self, sample: Sample) -> GradingResult:
        ...


@dataclass(frozen=True)
class ReliabilityBin:
    lower: float
    upper: float
    count: int
    avg_confidence: float
    avg_accuracy: float
    correct: int
