# makkAIng

Минимальный каркас backend-проекта для автоматической проверки ЕГЭ на FastAPI.

## Установка зависимостей

```bash
pip install -r requirements.txt
```

## Запуск сервера

```bash
uvicorn backend.app.main:app --reload
```

Сервер поднимется на http://127.0.0.1:8000, проверка `/ping` вернет `{"status": "ok"}`.

## Тесты

```bash
pytest
```
