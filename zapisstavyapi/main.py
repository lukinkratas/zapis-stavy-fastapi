from fastapi import FastAPI
from zapisstavyapi.routers.reading import router as reading_router

app = FastAPI()

app.include_router(reading_router)