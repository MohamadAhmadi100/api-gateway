from fastapi import HTTPException, Response, APIRouter, Request, Body, Query
# from source.helpers.rabbit_config import new_rpc
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.seller.validators.seller import Form
from source.services.seller import seller_controller as form_controller

router = APIRouter()


@router.post("/send_data")
def request_form_seller(form: Form, response: Response):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        request_form_result = rpc.publish(
            message=
            form_controller.seller_form_request(
                name=form.first_name,
                last_name=form.last_name,
                mobile_number=form.mobile_number,
                address=form.address,
                seller_status=form.seller_status,
                shipment=form.shipment_method,
                product_warehouse=form.product_warehouse,
                payment_method=form.payment_method,
                national_id=form.national_id
            ),
            headers={"seller": True}
        ).get("seller", {})
        if not request_form_result.get("success"):
            raise HTTPException(status_code=request_form_result.get("status_code", 500),
                                detail={"error": request_form_result.get("error", "Something went wrong")})
