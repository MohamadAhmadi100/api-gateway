import uvicorn
from fastapi import FastAPI

from source.routers.cart.app import app as cart_app
from config import settings

app = FastAPI(title="API Gateway",
              description="Backend for frontend aka. API Gateway!",
              version="0.0.1")

# ----------------------------------------- Mount all services here -------------------------------------------------- #

app.mount("/cart", cart_app)

# ----------------------------------------- Mount all services here -------------------------------------------------- #


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.UVICORN_HOST, port=settings.UVICORN_PORT, reload=True)
