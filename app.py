from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "BaytAI is live"}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}
