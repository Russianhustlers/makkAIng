# AGENTS

Назначение: прототип автоматической проверки рукописных решений с возможностью подменять бэкенд (LLM/заглушка).

Правила оформления
- Все поясняющие записи (комментарии, docstring, сообщения) пишем на русском.
- Добавляем комментарии там, где логика может быть неочевидной.

Ключевые модули
- `backend/grading/types.py` — `Sample`/`GradingResult`, протокол `GradingBackend`.
- `backend/grading/backends/dummy_backend.py` — детерминированная заглушка.
- `backend/grading/pipeline.py` — загрузка датасета задачи и прогон бэкенда.
- `backend/analysis` — метрики и графики калибровки.

Запуск «из коробки»
- Демо без данных: `python -m backend.grading.demo` > создаст `data/processed/demo_task` и запишет `results/demo_run.jsonl`.
- Быстрая проверка API: `uvicorn backend.app.main:app --reload` и GET `http://127.0.0.1:8000/ping`.

Свои данные
- Структура `data/processed/<task_id>/`: `images/`, `labels.csv` (student_id,true_score,max_score[,image_filename,solution_text,meta]), `statement.txt`, `rubric.txt`.
- Запуск пайплайна:
  ```python
  from pathlib import Path
  from backend.grading.backends.dummy_backend import DummyBackend
  from backend.grading.pipeline import run_task_directory

  run_task_directory(Path("data/processed/task_01"), DummyBackend(), experiment_name="task01", results_dir=Path("results"))
  ```
- Результаты всегда в `results/<experiment>.jsonl`.

Расширение
- Новый бэкенд должен реализовать `grade(sample: Sample) -> GradingResult` и атрибуты `name/model_name`.
- Сохраняйте детерминированность через seed и логируйте метаданные (`backend_name`, `timestamp`) для экспериментов.
