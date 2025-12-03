from fastapi import FastAPI

app = FastAPI(title="makkAIng API")


@app.get("/ping")
def ping():
    return {"status": "ok"}
