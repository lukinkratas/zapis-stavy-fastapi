from fastapi import FastAPI

from zapisstavyapi.routers.utility import router as reading_router

app = FastAPI()

app.include_router(reading_router)
