from fastapi import FastAPI, HTTPException

from source.config import settings
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
    redoc_url="/api/v1/redoc/",
    debug=settings.DEBUG_MODE
)

rpc = RabbitRPC(exchange_name='headers_exchange', timeout=5)
rpc.connect()
rpc.consume()


@app.put("/api/v1/cart/", status_code=202, tags=["Cart"])
def and_and_edit_product(item: AddCart) -> dict:
    """
    add and edit item in cart
    """
    # get user from token
    user = {"user_id": 0}
    rpc.response_len_setter(response_len=3)
    # check if all will have response(timeout)
    result = rpc.publish(
        message={"system_code": item.system_code, "user": user, "storage_id": item.storage_id, "count": item.count},
        headers={'product': True, 'pricing': True, 'quantity': True, 'action': 'get'}
    )
    if result.get("error"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    product_detail = result.get("product")
    product_detail["price"] = result.get("price")
    product_detail["warehouse"] = result.get("quantity")
    data_for_cart = {"user": user, "product": product_detail}
    rpc.response_len_setter(response_len=1)
    new_result = rpc.publish(
        message=data_for_cart,
        headers={'cart': True, 'action': 'add'}
    )
    if result.get("error"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return new_result

@app.get("/api/v1/cart/", status_code=200, tags=["Cart"])
def get_cart() -> dict:
    rpc.response_len_setter(response_len=1)
    # check if all will have response(timeout)
    result = rpc.publish(
        message={},
        headers={'cart': True, 'action': 'get'}
    )
    return result