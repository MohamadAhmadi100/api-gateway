from fastapi import FastAPI, HTTPException, Response, responses, Query
from starlette.exceptions import HTTPException as starletteHTTPException
from source.config import settings
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.payment.controllers.bank_controller import get_url
from source.routers.uis.validators.uis import Uis
from source.helpers.case_converter import convert_case

TAGS = [
    {
        "name": "UIS",
        "description": "Url Interface Endpoints"
    }
]

app = FastAPI(
    title="UIS API",
    description="This is UIS MicroService",
    version="0.1.0",
    openapi_tags=TAGS,
    docs_url="/docs/" if settings.DEBUG_MODE else None,
    redoc_url="/redoc/" if settings.DEBUG_MODE else None,
    debug=settings.DEBUG_MODE
)


@app.exception_handler(starletteHTTPException)
def validation_exception_handler(request, exc):
    return responses.JSONResponse(exc.detail, status_code=exc.status_code)


@app.post("/create")
def create_link(data: Uis, response: Response):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        request_service = {
            "payment": {
                "func": get_url,
                "data": ["amount", "service_id"]
            }
        }
        data.service_data = convert_case(data.service_data, "snake")
        service_data = dict()
        link_result = request_service.get(
            data.request_type, {}
        ).get("func")(
            data=data.service_data,
            response=response
        )
        if not link_result.get("success"):
            raise HTTPException(status_code=link_result.get("status_code", 500),
                                detail={"error": link_result.get("error", "Something went wrong")})
        service_datas = request_service.get(data.request_type, {}).get("data")
        for sr_data in service_datas:
            service_data[sr_data] = data.service_data.get(sr_data)
        rpc.response_len_setter(response_len=1)
        uis_result = rpc.publish(
            message={
                "uis": {
                    "action": "get_link_request",
                    "body": {
                        "request_service": data.request_type,
                        "service_data": service_data,
                        "link": link_result.get("message"),
                        "user_list": data.user_list,
                        "method_list": data.send_method_list,
                        "customer_id": data.customer_id
                    }
                }
            },
            headers={'uis': True}
        )
        uis_result = uis_result.get("uis", {})
        if not uis_result.get("success"):
            raise HTTPException(status_code=uis_result.get("status_code", 500),
                                detail={"error": uis_result.get("error", "Something went wrong")})
        response.status_code = uis_result.get("status_code")
        return {"message": uis_result.get("message")}


@app.get("/redirect")
def find_link(
        response: Response,
        key: str = Query(..., alias="key", regex='^.{8}$')
):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        uis_result = rpc.publish(
            message={
                "uis": {
                    "action": "find_links",
                    "body": {
                        "hashed_link": key
                    }
                }
            },
            headers={'uis': True}
        )
        uis_result = uis_result.get("uis", {})
        if not uis_result.get("success"):
            raise HTTPException(status_code=uis_result.get("status_code", 500),
                                detail={"error": uis_result.get("error", "Something went wrong")})
        response.status_code = uis_result.get("status_code", 200)
        return {"link": uis_result.get("message")}


@app.get("/data")
def get_data(
        response: Response,
        page: int = Query(1, ge=1, le=1000, alias="page"),
        per_page: int = Query(15, ge=1, le=1000, alias='perPage'),
):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        uis_result = rpc.publish(
            message={
                "uis": {
                    "action": "get_data",
                    "body": {
                        "page": page,
                        "per_page": per_page
                    }
                }
            },
            headers={'uis': True}
        )
        uis_result = uis_result.get("uis", {})
        if not uis_result.get("success"):
            raise HTTPException(status_code=uis_result.get("status_code", 500),
                                detail={"error": uis_result.get("error", "Something went wrong")})
        uis_result = uis_result.get("message")
        payment_result = rpc.publish(
            message={
                "payment": {
                    "action": "get_all_payment_by_service_id",
                    "body": {
                        "service_id": uis_result.get("service_id_list"),
                    }
                }
            },
            headers={'payment': True}
        ).get("payment", {})

        if not payment_result.get("success"):
            raise HTTPException(status_code=payment_result.get("status_code", 500),
                                detail={"error": payment_result.get("error", "Something went wrong")})
        payment_data = payment_result.get("message")
        for result in uis_result.get("data"):
            for res in payment_data:
                if result.get("serviceId") == res.get("serviceId"):
                    result.update(res)
                    break
        del uis_result["service_id_list"]
        response.status_code = payment_result.get("status_code")
        return uis_result
