from source.message_broker.rabbit_server import RabbitRPC
from fastapi import HTTPException
import source.services.customer.router_profile as profile_funcs
from source.helpers.rabbit_config import new_rpc


def get_profile_info(user_data: dict) -> dict or Exception:
    """
    matches request from user to get profile data, combines with customer attributes
    based on user data
    :param user_data: example: {'user_id': int, 'customer_type': list, 'phone_number': str'}
    :return: dict for response to client or HttpException for 422, 404 or 418 res
    """

    customer_data = new_rpc.publish(
        message=[profile_funcs.get_raw_profile(customer_phone_number=user_data.get("phone_number"))]
    )
    if not customer_data.get("success"):
        raise HTTPException(
            status_code=customer_data.get("status_code", 500),
            detail={"error": customer_data.get("error", "Something went wrong")}
        )
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        address_response = rpc.publish(
            message={
                "address": {
                    "action": "get_default_address",
                    "body": {
                        "customerId": str(user_data.get("user_id"))
                    }
                }
            },
            headers={'address': True}
        ).get("address", {})
        customer = customer_data.get("message")
        if not address_response.get("success"):
            return customer_data
        customer['customerAddress'] = address_response['result'].get("fullAddress")
        customer['customerCity'] = address_response['result'].get('cityName')
        customer['customerProvince'] = address_response['result'].get('stateName')
        customer['cityID'] = address_response['result'].get('cityId')
        customer['customerProvinceCode'] = address_response['result'].get('stateId')
    return customer
