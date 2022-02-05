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
def add_and_edit_product(item: AddCart) -> dict:
    """
    add and edit item in cart
    """
    # get user from token
    user = {"user_id": 0}
    rpc.response_len_setter(response_len=3)
    # check if all will have response(timeout)
    product_result = rpc.publish(
        message={
            "product": {
                "action": "get_product_by_system_code",
                "body": {
                    "system_code": item.system_code
                }
            },
            "pricing": {
                "action": "get_price_by_system_code",
                "body": {
                    "system_code": item.system_code,
                    "storage_id": item.storage_id,
                    "user": user
                }
            },
            "quantity": {
                "action": "get_quantity_by_system_code",
                "body": {
                    "system_code": item.system_code,
                    "storage_id": item.storage_id,
                    "count": item.count
                }
            }
        },
        headers={'product': True, 'pricing': True, 'quantity': True}
    )
    if product_result.get("error"):
        raise HTTPException(status_code=400, detail=product_result.get("error"))
    if product_result.get("product"):
        product_detail = product_result.get("product")
        product_detail["price"] = product_result.get("price")
        product_detail["warehouse"] = product_result.get("quantity")
        rpc.response_len_setter(response_len=1)
        cart_result = rpc.publish(
            message={
                "cart": {
                    "action": "add_to_cart",
                    "body": {
                        "user": user,
                        "product": product_detail
                    }
                }
            },
            headers={'cart': True}
        )
        if cart_result.get("error"):
            raise HTTPException(status_code=400, detail=cart_result.get("error"))
        else:
            return cart_result
    else:
        raise HTTPException(status_code=404, detail={"message": "product doesn't exists",
                                                     "label": "محصول موجود نیست",
                                                     "redirect": "/product/{system_code}"})


# @app.get("/api/v1/cart/", status_code=200, tags=["Cart"])
# def get_cart() -> dict:
#     rpc.response_len_setter(response_len=1)
#     # check if all will have response(timeout)
#     result = rpc.publish(
#         message={},
#         headers={'cart': True, 'action': 'get'}
#     )
#     return result
