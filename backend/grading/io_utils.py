"""Функции ввода-вывода: загрузка задач и сохранение результатов."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable, List

from backend.grading.types import GradingResult, Sample


def read_text_file(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Не найден обязательный текстовый файл: {path}")
    return path.read_text(encoding="utf-8").strip()


def load_labels(labels_path: Path) -> List[dict]:
    if not labels_path.exists():
        raise FileNotFoundError(f"Не найден labels.csv по пути {labels_path}")

    with labels_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"student_id", "true_score", "max_score"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"В labels.csv отсутствуют обязательные колонки: {missing}")

        labels: List[dict] = []
        for row in reader:
            labels.append(row)
    return labels


def resolve_image_path(image_root: Path, student_id: str, row: dict) -> Path:
    candidates = [
        row.get("image"),
        row.get("image_filename"),
        row.get("image_path"),
    ]

    # Дополнительные варианты имени файла, если в CSV нет явного пути.
    candidates.extend(
        [
            f"student_{student_id}.png",
            f"{student_id}.png",
            f"student_{student_id}.jpg",
            f"{student_id}.jpg",
        ]
    )

    for candidate in candidates:
        if not candidate:
            continue
        candidate_path = (image_root / candidate).resolve()
        if candidate_path.exists():
            return candidate_path

    raise FileNotFoundError(
        f"Не удалось найти изображение для student_id={student_id} в {image_root}. "
        "Укажите image_filename/image_path или соблюдайте шаблон student_XXXX.*."
    )


def load_samples(task_dir: Path, labels_filename: str = "labels.csv") -> List[Sample]:
    """
    Загрузить список Sample из каталога задачи.

    Ожидаемая структура:
      task_dir/
        statement.txt
        rubric.txt
        labels.csv
        images/
    """

    task_dir = task_dir.resolve()
    statement_text = read_text_file(task_dir / "statement.txt")
    rubric_text = read_text_file(task_dir / "rubric.txt")
    labels = load_labels(task_dir / labels_filename)
    images_root = task_dir / "images"

    samples: List[Sample] = []
    for row in labels:
        student_id = str(row["student_id"]).zfill(4)
        true_score = int(row["true_score"])
        max_score = int(row["max_score"])

        image_path = resolve_image_path(images_root, student_id, row)

        sample: Sample = {
            "task_id": task_dir.name,
            "student_id": student_id,
            "image_path": str(image_path),
            "statement_text": statement_text,
            "rubric_text": rubric_text,
            "true_score": true_score,
            "max_score": max_score,
        }

        if "solution_text" in row and row["solution_text"]:
            sample["solution_text"] = row["solution_text"]
        if "meta" in row and row["meta"]:
            try:
                sample["meta"] = json.loads(row["meta"])
            except json.JSONDecodeError:
                sample["meta"] = {"raw": row["meta"]}

        samples.append(sample)

    return samples


def save_results_jsonl(results: Iterable[GradingResult], output_path: Path, metadata: dict | None = None) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        for result in results:
            merged = dict(metadata or {})
            merged.update(result)
            f.write(json.dumps(merged, ensure_ascii=False) + "\n")
    return output_path
