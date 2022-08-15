# important import... don't remove this at home(even you dear friend)
import source.services.invoker
import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from source.routers.uis.app import app as uis_app
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
from source.routers.address.app import app as address_app
from source.routers.shipment.app import app as shipment_app
from source.routers.order.app import app as order_app
from source.routers.mobile_app.app import app as mobile_app
from source.routers.dealership.app import app as dealership
from source.routers.credit.app import app as credit_app
from fastapi_utils.tasks import repeat_every
# from source.routers.payment.modules.payment_callback import closing_tab_handling

app = FastAPI(title="API Gateway",
              description="Backend for frontend aka. API Gateway!",
              version="0.0.1")
# app.middleware()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# ----------------------------------------- Mount all services here -------------------------------------------------- #

app.mount("/cart/api/v1", cart_app)

app.mount("/pricing/api/v1", pricing_app)

app.mount("/quantity/api/v1", quantity_app)

app.mount("/product/api/v1", product_app)

app.mount("/customer/api/v1", customer_app)

app.mount("/wallet/api/v1", wallet_app)

app.mount("/attributes/api/v1", attribute_app)

app.mount("/payment/api/v1", payment_app)

app.mount("/coupon", coupon_app)

app.mount("/gallery/api/v1", gallery_app)

app.mount("/gallery_files/", StaticFiles(directory=settings.GALLERY_DIR), name="gallery_files")

app.mount("/address/api/v1", address_app)

app.mount("/shipment/api/v1", shipment_app)

app.mount("/order/api/v1", order_app)

app.mount("/mobile_app/api/v1", mobile_app)

app.mount("/dealership/api/v1", dealership)

app.mount("/credit/api/v1", credit_app)

app.mount("/uis/api/v1", uis_app)


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


#@app.on_event("startup")
#@repeat_every(seconds=60)
#def payment_close_tab_handler():
#    closing_tab_handling()


@app.get("/")
def main():
    return [{"path": f"https://devapi.aasood.com{route.path}/docs/"} for route in app.routes][4:-1]


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.UVICORN_HOST, port=settings.UVICORN_PORT, reload=True, workers=12)
