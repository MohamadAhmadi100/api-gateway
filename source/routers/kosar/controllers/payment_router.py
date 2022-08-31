from fastapi import Response, APIRouter, Query, HTTPException
from source.helpers.case_converter import convert_case
from source.message_broker.rabbit_server import RabbitRPC
import source.services.kosar.payment_controller as kosar_service

router = APIRouter()


@router.get("/get_kosar")
def get_kowsar_result(response: Response, service_id: str = Query(..., alias="serviceId")):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        kosar_data = rpc.publish(
            message=kosar_service.get_kowsar_data(service_id=service_id),
            headers={"kosar": True}
        ).get("kosar", {})
        if not kosar_data.get("success"):
            raise HTTPException(status_code=kosar_data.get("status_code", 500),
                                detail={"error": kosar_data.get("error", "Something went wrong")})
        response.status_code = kosar_data.get("status_code")
        return convert_case(kosar_data.get("message"), 'camel')

