from fastapi import FastAPI

app = FastAPI(
    title="CounselAI-Pro",
    version="0.1.0",
    description="A world-class legal contract analysis microservice.",
)


@app.get("/")
async def root():
    return {"project": "CounselAI-Pro", "version": "0.1.0"}