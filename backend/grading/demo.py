"""Самостоятельный демо-скрипт для проверки пайплайна целиком."""

from __future__ import annotations

import random
from pathlib import Path
from typing import Tuple

from backend.grading.backends.dummy_backend import DummyBackend
from backend.grading.pipeline import run_task_directory


def generate_dummy_task(task_dir: Path, num_samples: int = 5, max_score: int = 3) -> Path:
    """
    Создаёт минимальный набор данных с синтетическими метками и заглушками изображений.

    Вместо реальных картинок используются текстовые файлы, чтобы не тянуть зависимости.
    """

    task_dir = task_dir.resolve()
    images_dir = task_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    (task_dir / "statement.txt").write_text(
        "Solve the quadratic equation x^2 - 5x + 6 = 0. Show your work.", encoding="utf-8"
    )
    (task_dir / "rubric.txt").write_text(
        "Full solution with both roots: full credit. Partial algebra: partial credit.", encoding="utf-8"
    )

    rows = ["student_id,true_score,max_score,image_filename"]
    for idx in range(1, num_samples + 1):
        student_id = f"{idx:04d}"
        true_score = random.randint(0, max_score)
        filename = f"student_{student_id}.png"
        rows.append(f"{student_id},{true_score},{max_score},{filename}")
        (images_dir / filename).write_text("placeholder image bytes", encoding="utf-8")

    (task_dir / "labels.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")
    return task_dir


def run_demo(base_dir: Path | str = "data/processed/demo_task", experiment_name: str = "demo_run") -> Tuple[str, Path]:
    """
    Генерирует задачу-заглушку, прогоняет DummyBackend и сохраняет JSONL с результатами.

    Возвращает (experiment_name, output_path).
    """

    task_dir = Path(base_dir)
    generate_dummy_task(task_dir)
    backend = DummyBackend(seed="demo-seed")
    results, output_path = run_task_directory(task_dir, backend, experiment_name=experiment_name, results_dir=Path("results"))
    return experiment_name, output_path


if __name__ == "__main__":
    name, path = run_demo()
    print(f"Демо-эксперимент '{name}' завершён. Результаты сохранены в: {path}")
