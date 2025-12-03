"""Детерминированная заглушка, имитирующая работу LLM-грейдера."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Optional

from backend.grading.types import GradingBackend, GradingResult, Sample


class DummyBackend(GradingBackend):
    """
    Правил-бейзед бэкенд, заменяющий реальную мультимодальную модель на этапе разработки.

    Балл выводится из хэша идентификаторов задачи и ученика, поэтому результат устойчив
    между запусками, но остаётся не тривиальным.
    """

    name = "dummy_v1"
    model_name = "dummy_v1"

    def __init__(self, seed: Optional[str] = None, base_confidence: float = 0.65, noise: float = 0.2):
        self.seed = seed or "seedless"
        self.base_confidence = base_confidence
        self.noise = noise

    def _score_fraction(self, sample: Sample) -> float:
        """Получить дробь 0..1 из хэша, чтобы балл был воспроизводимым."""
        key = f"{sample['task_id']}|{sample['student_id']}|{self.seed}"
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
        return (int(digest[:8], 16) % 1000) / 999

    def grade(self, sample: Sample) -> GradingResult:
        fraction = self._score_fraction(sample)
        predicted_score = round(fraction * sample["max_score"])
        predicted_score = max(0, min(sample["max_score"], predicted_score))

        # Чем дальше прогноз от истинного балла, тем ниже уверенность.
        distance = abs(predicted_score - sample["true_score"]) / max(sample["max_score"], 1)
        confidence = max(0.05, min(1.0, self.base_confidence + self.noise * (0.5 - distance)))

        comment = (
            "Детерминированная заглушка; меняйте seed или подсказку, чтобы варьировать ответ. "
            f"Часть хэша={fraction:.2f}, отклонение от истинного балла={distance:.2f}."
        )

        return {
            "student_id": sample["student_id"],
            "task_id": sample["task_id"],
            "true_score": sample["true_score"],
            "max_score": sample["max_score"],
            "pred_score": predicted_score,
            "confidence": round(confidence, 3),
            "comment": comment,
            "backend_name": self.name,
            "model_name": self.model_name,
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "raw_response": {
                "strategy": "hash_det",
                "seed": self.seed,
                "fraction": fraction,
            },
        }
