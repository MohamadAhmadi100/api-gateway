from source.message_broker.rabbit_server import RabbitRPC
from fastapi import HTTPException

rpc = RabbitRPC(exchange_name='headers_exchange', timeout=5)
rpc.connect()
rpc.consume()


def get_profile_info(user_data: dict) -> dict or Exception:
    """
    matches request from user to get profile data, combines with customer attributes
    based on user data
    :param user_data: example: {'user_id': int, 'customer_type': list, 'phone_number': str'}
    :return: dict for response to client or HttpException for 422, 404 or 418 res
    """
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
    valid_attrs = []
    for attr in attributes:
        if customer_data.get(attr.get("name")) is None or not None:
            attr["value"] = customer_data.get(attr.get("name"))
            valid_attrs.append(attr)
    return valid_attrs
