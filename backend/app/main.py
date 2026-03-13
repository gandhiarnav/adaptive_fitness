from fastapi import FastAPI

app = FastAPI(title="Adaptive Fitness Backend")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Adaptive Fitness API!"}