from fastapi import FastAPI, Response, HTTPException
from fastapi import responses as f_responses
from starlette.exceptions import HTTPException as starletteHTTPException
from source.routers.cart.validators.cart import Cart

TAGS = [
    {
        "name": "Cart",
        "description": "Cart CRUD"
    }
]
cart = FastAPI(
    title="Cart API",
    description="This is Cart gateway MicroService",
    version="0.1.0",
    openapi_tags=TAGS,
    docs_url="/docs/"
)


@cart.put("/cart/", status_code=202, tags=["Cart"])
def edit_and_add_product_in_cart(item: Cart, responses: Response) -> dict:
    """
    edit and add item in cart
    """
    response = item.add_to_cart()
    if type(response) is tuple:
        message, status = response
        if status == 'delete':
            responses.status_code = 200
            return message
        raise HTTPException(status_code=417, detail=message)
    return response


@cart.delete("/cart/{system_code}/{user_id}/{storage_id}", status_code=200, tags=["Cart"])
def remove_product_from_cart(system_code: str, user_id: int, storage_id: str) -> dict:
    """
    remove an item from cart

    """
    response = Cart.remove_from_cart(system_code, user_id, storage_id)
    if response:
        return response
    raise HTTPException(status_code=404, detail={'error': 'product not found'})


@cart.get("/cart/{user_id}/", status_code=200, tags=["Cart"])
def get_cart(user_id: int) -> dict:
    """
    get user cart
    """
    cart = Cart.construct()
    stored_data = cart.get_cart(user_id)
    if stored_data:
        return stored_data.dict()
    raise HTTPException(status_code=404, detail={'error': 'cart not found'})


@cart.exception_handler(starletteHTTPException)
def validation_exception_handler(request, exc):
    return f_responses.JSONResponse(exc.detail, status_code=exc.status_code)
