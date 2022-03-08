import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from source.routers.cart.app import app as cart_app
from source.routers.pricing.app import app as pricing_app
from source.routers.product.app import app as product_app
from source.routers.quantity.app import app as quantity_app
from source.routers.customer.app import app as customer_app
from source.routers.wallet.app import app as wallet_app
from source.routers.attribute.app import app as attribute_app
from source.routers.payment.app import app as payment_app
from source.routers.coupon.app import app as coupon_app
from source.routers.gallery.app import app as gallery_app


app = FastAPI(title="API Gateway",
              description="Backend for frontend aka. API Gateway!",
              version="0.0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------- Mount all services here -------------------------------------------------- #

app.mount("/cart", cart_app)

app.mount("/pricing/api/v1", pricing_app)

app.mount("/quantity/api/v1", quantity_app)

app.mount("/product/api/v1", product_app)

app.mount("/customer", customer_app)

app.mount("/wallet", wallet_app)

app.mount("/attributes", attribute_app)

app.mount("/payment", payment_app)

app.mount("/coupon", coupon_app)

app.mount("/gallery", gallery_app)


# ----------------------------------------- Start logging features  -------------------------------------------------- #

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


@app.get("/")
def main():
    return [{"path": "https://devapi.aasood.com" + route.path + "/docs/"}
            for route in app.routes][4:-1]


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.UVICORN_HOST, port=settings.UVICORN_PORT, reload=True)
