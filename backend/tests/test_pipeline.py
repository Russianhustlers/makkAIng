import json
from pathlib import Path

from backend.grading.backends.dummy_backend import DummyBackend
from backend.grading.io_utils import load_samples
from backend.grading.pipeline import run_task_directory


def make_task(tmp_path: Path) -> Path:
    task_dir = tmp_path / "data" / "processed" / "task_01"
    images_dir = task_dir / "images"
    images_dir.mkdir(parents=True)

    (task_dir / "statement.txt").write_text("Найдите производную функции x^2", encoding="utf-8")
    (task_dir / "rubric.txt").write_text("Полное решение: 2 балла; частичное: 1 балл", encoding="utf-8")

    labels = "student_id,true_score,max_score,image_filename\n0001,2,2,student_0001.png\n0002,1,2,student_0002.png\n"
    (task_dir / "labels.csv").write_text(labels, encoding="utf-8")

    for name in ("student_0001.png", "student_0002.png"):
        (images_dir / name).write_text("заглушка изображения", encoding="utf-8")

    return task_dir


def test_load_samples_reads_context(tmp_path):
    task_dir = make_task(tmp_path)

    samples = load_samples(task_dir)

    assert len(samples) == 2
    assert samples[0]["statement_text"] == "Найдите производную функции x^2"
    assert samples[0]["rubric_text"].startswith("Полное решение")
    assert Path(samples[0]["image_path"]).exists()


def test_dummy_backend_pipeline_writes_jsonl(tmp_path):
    task_dir = make_task(tmp_path)
    results_dir = tmp_path / "results"
    backend = DummyBackend(seed="test-seed")

    results, output_path = run_task_directory(task_dir, backend, experiment_name="demo_exp", results_dir=results_dir)

    assert len(results) == 2
    assert output_path.exists()

    lines = output_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    parsed = json.loads(lines[0])
    assert parsed["backend_name"] == backend.name
    assert "pred_score" in parsed and "confidence" in parsed
