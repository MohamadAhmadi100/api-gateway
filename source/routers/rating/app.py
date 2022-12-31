from source.message_broker.rabbit_server import RabbitRPC
from source.config import settings
from source.routers.customer.module.auth import AuthHandler
from source.routers.rating.validator.rate_wallidator import InsertRate
from fastapi import HTTPException, Response, Depends, APIRouter, FastAPI

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


@app.post("/insert-rate", tags=["customer side"])
def insert_rate(data: InsertRate, response: Response,
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
                    "action": "create_new_rate",
                    "body": {
                        "system_code": data.system_code,
                        "sku": data.sku,
                        "customer_id": data.customer_id,
                        "customer_name": data.customer_name,
                        "customer_type": data.customer_type,
                        "seller_id": data.seller_id,
                        "seller_name": data.seller_name,
                        "details": data.details,
                        "properties": data.properties,
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
