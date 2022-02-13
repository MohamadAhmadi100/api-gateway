from fastapi import FastAPI, HTTPException, Response, responses, Path
from starlette.exceptions import HTTPException as starletteHTTPException

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


# customize exception handler of fast api
@app.exception_handler(starletteHTTPException)
def validation_exception_handler(request, exc):
    return responses.JSONResponse(exc.detail, status_code=exc.status_code)


# initialize rabbit mq
rpc = RabbitRPC(exchange_name='headers_exchange', timeout=5)
rpc.connect()
rpc.consume()


@app.put("/api/v1/cart/", tags=["Cart"])
def add_and_edit_product(item: AddCart, response: Response) -> dict:
    """
    add and edit item in cart
    edit is based on product count and warehouse id
    """
    # get user from token
    user = {"user_id": 0}
    rpc.response_len_setter(response_len=3)
    result = rpc.publish(
        message={
            "product": {
                "action": "get_product_by_system_code",
                "body": {
                    "system_code": item.parent_system_code,
                    "lang": "fa_ir"
                }
            }, "pricing": {
                "action": "get_price",
                "body": {
                    "system_code": item.parent_system_code
                }
            }, "quantity": {
                "action": "get_quantity",
                "body": {
                    "system_code": item.parent_system_code
                }
            }
        },
        headers={'product': True, "pricing": True, "quantity": True}
    )
    product_result = result.get("product", {})
    pricing_result = result.get("pricing", {})
    quantity_result = result.get("quantity", {})
    if not product_result.get("success"):
        raise HTTPException(status_code=product_result.get("status_code", 500),
                            detail={"error": product_result.get("error", "Something went wrong")})
    elif not pricing_result.get("success"):
        raise HTTPException(status_code=pricing_result.get("status_code", 500),
                            detail={"error": pricing_result.get("error", "Something went wrong")})
    elif not quantity_result.get("success"):
        raise HTTPException(status_code=quantity_result.get("status_code", 500),
                            detail={"error": quantity_result.get("error", "Something went wrong")})
    else:
        product_result = product_result.get("message").copy()
        final_result = dict()
        final_result["user_info"] = user
        for product in product_result.get("products", []):
            if product.get("system_code") == item.system_code:
                final_result["product"] = product
                break
        for price in pricing_result.get("message", {}).get("products", {}).get(item.system_code, {}).get(
                "customer_type").get("B2B").get("storages", []):
            if price.get("storage_id") == item.storage_id:
                final_result["price"] = price.get("special") if price.get("special") else price.get("regular")
                break
        for quantity in quantity_result.get("message", {}).get("products", {}).get(item.system_code, {}).get(
                "customer_types").get("B2B").get("storages", []):
            if quantity.get("storage_id") == item.storage_id:
                if quantity.get("stock_for_sale") > item.count:
                    final_result["count"] = item.count
                    final_result["storage_id"] = item.storage_id
                    break
                else:
                    raise HTTPException(status_code=400,
                                        detail={"error": "Not enough quantity"})
        rpc.response_len_setter(response_len=1)
        cart_result = rpc.publish(
            message={
                "cart": {
                    "action": "add_and_edit_product_in_cart",
                    "body": {
                        "user_info": final_result.get("user_info"),
                        "product": final_result.get("product"),
                        "price": final_result.get("price"),
                        "count": final_result.get("count"),
                        "storage_id": final_result.get("storage_id")
                    }
                }
            },
            headers={'cart': True}
        )
        cart_result = cart_result.get("cart", {})
        if not cart_result.get("success"):
            raise HTTPException(status_code=product_result.get("status_code", 500),
                                detail={"error": product_result.get("error", "Something went wrong")})
        else:
            response.status_code = cart_result.get("status_code", 200)
            return cart_result.get("message")


@app.get("/api/v1/cart/{user_id}/", tags=["Cart"])
def get_cart(response: Response, user_id: int = Path(..., ge=0, lt=80_000_000)) -> dict:
    """
    get user cart
    """
    rpc.response_len_setter(response_len=1)
    result = rpc.publish(
        message={
            "cart": {
                "action": "get_cart",
                "body": {
                    "user_id": user_id
                }
            }
        },
        headers={'cart': True}
    )
    cart_result = result.get("cart", {})
    if not cart_result.get("success"):
        raise HTTPException(status_code=cart_result.get("status_code", 500),
                            detail={"error": cart_result.get("error", "Something went wrong")})
    else:
        response.status_code = cart_result.get("status_code", 200)
        return cart_result.get("message")


@app.delete("/api/v1/cart/{system_code}/{user_id}/{storage_id}", status_code=200, tags=["Cart"])
def remove_product_from_cart(response: Response, user_id: int = Path(..., ge=0, lt=80_000_000),
                             storage_id: str = Path(..., min_length=1, max_length=2),
                             system_code: str = Path(..., min_length=12, max_length=12)) -> dict:
    """
    remove an item from cart
    """
    rpc.response_len_setter(response_len=1)
    result = rpc.publish(
        message={
            "cart": {
                "action": "remove_product_from_cart",
                "body": {
                    "user_id": user_id,
                    "system_code": system_code,
                    "storage_id": storage_id
                }
            }
        },
        headers={'cart': True}
    )
    cart_result = result.get("cart", {})
    if not cart_result.get("success"):
        raise HTTPException(status_code=cart_result.get("status_code", 500),
                            detail={"error": cart_result.get("error", "Something went wrong")})
    else:
        response.status_code = cart_result.get("status_code", 200)
        return cart_result.get("message")
