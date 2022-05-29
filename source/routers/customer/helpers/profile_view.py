from source.message_broker.rabbit_server import RabbitRPC
from fastapi import HTTPException


def get_profile_info(user_data: dict) -> dict or Exception:
    """
    matches request from user to get profile data, combines with customer attributes
    based on user data
    :param user_data: example: {'user_id': int, 'customer_type': list, 'phone_number': str'}
    :return: dict for response to client or HttpException for 422, 404 or 418 res
    """
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        result = rpc.publish(
            message={
                "customer": {
                    "action": "get_profile",
                    "body": {
                        "customer_phone_number": user_data,
                    }
                }
            },
            headers={'customer': True}
        )
    customer_result = result.get("customer", {})
    if not customer_result.get("success"):
        raise HTTPException(
            status_code=customer_result.get("status_code", 500),
            detail={"error": customer_result.get("error", "Something went wrong")}
        )

    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        result = rpc.publish(
            message={
                "attribute": {
                    "action": "get_all_attributes_by_assignee",
                    "body": {
                        "name": "customer"
                    }
                }
            },
            headers={'attribute': True}
        )
        attribute_result = result.get("attribute", {})
    if not attribute_result.get("success"):
        raise HTTPException(status_code=attribute_result.get("status_code", 500),
                            detail={"error": attribute_result.get("error", "Something went wrong")})
    customer_data = customer_result.get("message", {})
    attributes = attribute_result.get("message", [])
    for attr in attributes:
        if customer_data.get(attr.get("name")) is None or not None:
            attr["value"] = customer_data.get(attr.get("name"))
            customer_data[attr['name']] = attr['value']
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        address_response = rpc.publish(
            message={
                "address": {
                    "action": "get_customer_addresses",
                    "body": {
                        "customerId": str(user_data.get("user_id"))
                    }
                }
            },
            headers={'address': True}
        ).get("address", {})
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

        if not address_response.get("success"):
            return customer_data
        else:
            customer_data['customerAddress'] = address_response['result'].get("fullAddress")
            customer_data['customerCity'] = address_response['result'].get('cityName')
            customer_data['customerProvince'] = address_response['result'].get('stateName')
            customer_data['cityID'] = address_response['result'].get('cityId')
            customer_data['customerProvinceCode'] = address_response['result'].get('stateId')
    return customer_data
