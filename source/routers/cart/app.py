from fastapi import FastAPI

from source.message_broker.rabbit_server import RabbitRPC
from source.routers.cart.validators.cart import AddCart

TAGS = [
    {
        "name": "Cart",
        "description": "Cart CRUD"
    }
]
app = FastAPI(
    title="Cart API",
    description="This is Cart gateway MicroService",
    version="0.1.0",
    openapi_tags=TAGS,
    docs_url="/api/v1/docs/",
    redoc_url="/api/v1/redoc/"
)

rpc = RabbitRPC(sending_queue='cart_queue')
rpc.connect()
rpc.consume()


@app.put("/api/v1/cart/", status_code=202, tags=["Cart"])
def and_and_edit_product(item: AddCart) -> dict:
    """
    add and edit item in cart
    """
    item.user_id = 10101010101

    rpc.publish(item.dict())
    return rpc.response
