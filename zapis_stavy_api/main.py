from fastapi import FastAPI

app = FastAPI()


@app.get('/')
async def root() -> dict[str, str]:
    """Example root."""
    return {'message': 'Hello World'}
