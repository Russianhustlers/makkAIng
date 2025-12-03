# makkAIng

Прототип автоматической проверки рукописных решений задач ЕГЭ по математике с LLM-совместимым интерфейсом и заглушкой для офлайн-разработки.

## Что здесь есть
- FastAPI-приложение (`backend/app`) с эндпоинтом `/ping` для проверки живости.
- Пайплайн проверки (`backend/grading`): типы, загрузка данных, бэкенды, запуск по каталогу задачи.
- Аналитика (`backend/analysis`): метрики качества и калибровки, построение графиков.
- Папки для данных (`data/raw`, `data/processed`), результатов (`results`), ноутбуков (`notebooks`).

## Быстрый старт
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m pytest
```

Запуск API локально:
```bash
uvicorn backend.app.main:app --reload
```
Проверка: `http://127.0.0.1:8000/ping` возвращает `{ "status": "ok" }`.

## Демо без подготовки данных
1) Выполнить:
```bash
python -m backend.grading.demo
```
2) Скрипт сам создаст `data/processed/demo_task` с заглушками изображений и метками, прогонит `DummyBackend`, сохранит `results/demo_run.jsonl`.
3) Посмотреть результат:
```bash
type results\demo_run.jsonl
```

## Подготовка своих данных
Структура одной задачи:
```
data/processed/task_01/
  images/
    student_0001.png
    student_0002.png
  labels.csv          # обязательные колонки: student_id,true_score,max_score; опционально: image_filename,solution_text,meta
  statement.txt       # текст условия задачи
  rubric.txt          # текст критериев оценивания
```
Советы:
- Если в `labels.csv` есть колонка `image_filename` или `image_path`, она используется для поиска файла. Иначе ожидается шаблон `student_<id>.png` / `student_<id>.jpg` в `images/`.
- `meta` можно положить как JSON-строку, она попадёт в `Sample.meta`.

## Запуск пайплайна на своих данных
Пример на Python:
```python
from pathlib import Path
from backend.grading.backends.dummy_backend import DummyBackend
from backend.grading.pipeline import run_task_directory

backend = DummyBackend(seed="demo-seed")
results, output_path = run_task_directory(
    task_dir=Path("data/processed/task_01"),
    backend=backend,
    experiment_name="task01_dummy",
    results_dir=Path("results"),
)
print(f"Сохранено в {output_path}")
```
Выход: JSONL в `results/<experiment>.jsonl` со строками вида `student_id,true_score,pred_score,confidence,comment,backend_name,timestamp,...`.

## Анализ
- Метрики: `backend/analysis/metrics.py` (accuracy, MAE, квадратическая каппа, reliability curve, зависимость точности от порога уверенности).
- Графики: `backend/analysis/plots.py` (reliability diagram), требует `matplotlib`.

## Расширение
Бэкенды реализуют протокол `grade(sample: Sample) -> GradingResult` (`backend/grading/types.py`). Можно заменить `DummyBackend` на реальный вызов LLM без изменения пайплайна.
