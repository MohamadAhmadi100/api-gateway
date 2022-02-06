import logging

import uvicorn
from fastapi import FastAPI

from config import settings
from source.routers.cart.app import app as cart_app
from source.routers.pricing.app import app as pricing_app
from source.routers.product.app import app as product_app
from source.routers.quantity.app import app as quantity_app

app = FastAPI(title="API Gateway",
              description="Backend for frontend aka. API Gateway!",
              version="0.0.1")

# ----------------------------------------- Mount all services here -------------------------------------------------- #

app.mount("/cart", cart_app)

app.mount("/pricing", pricing_app)

app.mount("/quantity", quantity_app)

app.mount("/product", product_app)


# ----------------------------------------- Mount all services here -------------------------------------------------- #

@app.on_event("startup")
async def startup_event() -> None:
    """
    This function will be called when the application starts.
    """
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        filename="app.log",
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logging.info("Application is starting...")


@app.on_event("shutdown")
def shutdown_event() -> None:
    """
    This function will be called when the application stops.
    """
    logging.info("Application is shutting down...")


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.UVICORN_HOST, port=settings.UVICORN_PORT, reload=True)
