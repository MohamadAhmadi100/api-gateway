from typing import Union

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Query
from fastapi import Response, Depends
from starlette.exceptions import HTTPException

from source.message_broker.rabbit_server import RabbitRPC
from source.routers.customer.module.auth import AuthHandler

get_order = APIRouter()

auth_handler = AuthHandler()


@get_order.get("/orders_list/", tags=["Get orders"])
def get_all_orders(response: Response,
                   page: Union[int, None] = Query(default=1),
                   perPage: Union[int, None] = Query(default=15),
                   orderNumber: Union[int, None] = Query(default=None),
                   dateFrom: Union[str, None] = Query(default=None),
                   dateTo: Union[str, None] = Query(default=None),
                   invStore: Union[str, None] = Query(default=None),
                   auth_header=Depends(auth_handler.check_current_user_tokens)):
    user, token_dict = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        order_response = rpc.publish(
            message={
                "order": {
                    "action": "get_customer_orders",
                    "body": {
                        "customerId": user.get("user_id"),
                        "orderNumber": orderNumber,
                        "dateFrom": dateFrom,
                        "dateTo": dateTo,
                        "page": page,
                        "perPage": perPage,
                        "invStore": invStore,

                    }
                }
            },
            headers={'order': True}
        ).get("order", {})
        if order_response.get("success"):
            response.status_code = order_response.get("status_code", 200)
            return order_response
        raise HTTPException(status_code=order_response.get("status_code", 500),
                            detail={"error": order_response.get("error", "Order service Internal error")})
