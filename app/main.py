
from fastapi import FastAPI

# Create the application instance
app = FastAPI(
    title="FastAPI Learning API"
)

# GET METHOD + PATH: /
@app.get("/welcome")
def home():
    return {"message": "Welcome Our FastAPI learning Project"}


# GET METHOD + PATH: /health
@app.get("/health")
def health_check():
    return {"status": "ok"}
