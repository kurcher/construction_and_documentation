from fastapi import FastAPI
from storage.database import engine, Base
from api.routes import router

# Створення таблиць БД при запуску
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Messenger API - Lab 2",
    description="Minimal Reference Architecture with Message Status Tracking (Variant 2)",
    version="1.0.0"
)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)