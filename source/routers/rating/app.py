from source.message_broker.rabbit_server import RabbitRPC
from source.config import settings
from typing import Optional
from source.routers.customer.module.auth import AuthHandler
from source.routers.rating.validator.rate_wallidator import InsertRate, LikesParameters
from fastapi import HTTPException, Response, Depends, APIRouter, FastAPI, Query

TAGS = [
    {
        "name": "Rating",
        "description": "Rating application endpoints"
    }
]
app = FastAPI(
    title="Rating API service",
    description="This is Rating gateway MicroService",
    version="0.1.0",
    openapi_tags=TAGS,
    docs_url="/docs/" if settings.DEBUG_MODE else None,
    redoc_url="/redoc/" if settings.DEBUG_MODE else None,
    debug=settings.DEBUG_MODE
)

router = APIRouter()
auth = AuthHandler()


@app.get("/get-property", tags=["customer side"])
def get_property(response: Response,
                 # auth_header=Depends(auth.check_current_user_tokens)
                 ):
    # sub_data, token_data = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        # response.headers["accessToken"] = token_data.get("access_token")
        # response.headers["refreshToken"] = token_data.get("refresh_token")
        rpc.response_len_setter(response_len=1)
        rating_response = rpc.publish(
            message={
                "rating": {
                    "action": "get_all_property",
                    "body": {}
                }

            },
            headers={'rating': True}
        ).get("rating", {})

        if rating_response.get("success"):
            response.status_code = rating_response.get("status_code", 200)
            return rating_response
        elif not rating_response.get("success"):
            response.status_code = rating_response.get("status_code", 417)
            return rating_response
        raise HTTPException(status_code=rating_response.get("status_code", 500),
                            detail={"error": rating_response.get("error", "Wallet service Internal error")})


@app.put("/edit-likes", tags=["customer side"])
def edit_likes(
        response: Response,
        rate_id: int = Query(..., alias="rateId"),
        parameter: Optional[LikesParameters] = Query(..., alias="parameter"),

        # auth_header=Depends(auth.check_current_user_tokens)
):
    # sub_data, token_data = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        # response.headers["accessToken"] = token_data.get("access_token")
        # response.headers["refreshToken"] = token_data.get("refresh_token")
        rpc.response_len_setter(response_len=1)

        rating_response = rpc.publish(
            message={
                "rating": {
                    "action": "update_likes",
                    "body": {

                        "rate_id": rate_id,
                        "parameter": parameter
                    }
                }
            },
            headers={'rating': True}
        ).get("rating", {})

        if rating_response.get("success"):
            response.status_code = rating_response.get("status_code", 200)
            return rating_response
        elif not rating_response.get("success"):
            response.status_code = rating_response.get("status_code", 417)
            return rating_response
        raise HTTPException(status_code=rating_response.get("status_code", 500),
                            detail={"error": rating_response.get("error", "Wallet service Internal error")})


@app.post("/insert-rate", tags=["customer side"])
def insert_rate(data: InsertRate, response: Response,
                # auth_header=Depends(auth.check_current_user_tokens)
                ):
    # sub_data, token_data = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        # response.headers["accessToken"] = token_data.get("access_token")
        # response.headers["refreshToken"] = token_data.get("refresh_token")
        rpc.response_len_setter(response_len=1)
        data = data.get_insert_rate()
        rating_response = rpc.publish(
            message={
                "rating": {
                    "action": "create_new_rate",
                    "body": {
                        "system_code": data.get("system_code"),
                        "sku": data.get("sku"),
                        "customer_id": data.get("customer_id"),
                        "customer_name": data.get("customer_name"),
                        "customer_type": data.get("customer_type"),
                        "seller_id": data.get("seller_id"),
                        "seller_name": data.get("seller_name"),
                        "details": data.get("details", {}),
                    }
                }
            },
            headers={'rating': True}
        ).get("rating", {})

        if rating_response.get("success"):
            response.status_code = rating_response.get("status_code", 200)
            return rating_response
        elif not rating_response.get("success"):
            response.status_code = rating_response.get("status_code", 417)
            return rating_response
        raise HTTPException(status_code=rating_response.get("status_code", 500),
                            detail={"error": rating_response.get("error", "Wallet service Internal error")})


@app.get("/product-rate", tags=["customer side"])
def get_products_rates(response: Response,
                       system_code: str = Query(..., alias="systemCode"),
                       page: int = Query(..., alias="page"),
                       per_page: int = Query(..., alias="perPage")
                       ):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        rating_response = rpc.publish(
            message={
                "rating": {
                    "action": "get_products_rates",
                    "body": {
                        "system_code": system_code,
                        "page": page,
                        "per_page": per_page,
                    }
                }
            },
            headers={'rating': True}
        ).get("rating", {})

        if rating_response.get("success"):
            response.status_code = rating_response.get("status_code", 200)
            return rating_response
        elif not rating_response.get("success"):
            response.status_code = rating_response.get("status_code", 417)
            return rating_response
        raise HTTPException(status_code=rating_response.get("status_code", 500),
                            detail={"error": rating_response.get("error", "Wallet service Internal error")})
