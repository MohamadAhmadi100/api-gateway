from fastapi import APIRouter

from fastapi import Response, Depends

from source.routers.cart.app import get_cart
from source.routers.customer.module.auth import AuthHandler
from source.routers.order.helpers.check_out import check_price_qty


first_step_order = APIRouter()

auth_handler = AuthHandler()


@first_step_order.get("/cart_detail/", tags=["get cart detail and checkout"])
def get_cart_detail(response: Response, auth_header=Depends(auth_handler.check_current_user_tokens)) -> dict:
    cart = get_cart(response=response, auth_header=auth_header)
    if not cart['products']:
        return {"success": True, "message": "سبد خرید خالی است"}
    check_out = check_price_qty(auth_header, cart, response)
    if check_out.get("success"):
        return {"success": True, "message": "checkout pass", "response": cart}
    else:
        cart = get_cart(response=response, auth_header=auth_header)
        return {"success": False, "message": check_out.get("message"), "response": cart}
