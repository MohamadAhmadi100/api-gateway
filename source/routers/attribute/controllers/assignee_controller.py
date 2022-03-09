from fastapi import Path, HTTPException, Response
from fastapi import APIRouter

from source.message_broker.rabbit_server import RabbitRPC
from source.routers.attribute.validators.assignee import Assignee

router = APIRouter()

# initialize rabbit mq
rpc = RabbitRPC(exchange_name='headers_exchange', timeout=5)
rpc.connect()
rpc.consume()


@router.post("/api/v1/assignee/attr/{attr_name}", tags=["assignee"], status_code=201)
def add_attribute_to_assignee(
        response: Response,
        item: Assignee,
        attr_name: str = Path(..., min_length=3, max_length=255)
) -> dict:
    """
    Add an attribute to assignee collection(if not existed, it will create one) in database.
    """
    rpc.response_len_setter(response_len=1)
    result = rpc.publish(
        message={
            "attribute": {
                "action": "add_attribute_to_assignee",
                "body": {
                    "item": item.dict(),
                    "attr_name": attr_name
                }
            }
        },
        headers={'attribute': True}
    )
    attribute_result = result.get("attribute", {})
    if not attribute_result.get("success"):
        raise HTTPException(status_code=attribute_result.get("status_code", 500),
                            detail={"error": attribute_result.get("error", "Something went wrong")})
    else:
        product_result = rpc.publish(
            message={
                "product": {
                    "action": "update_attribute_collection",
                    "body": {
                        "attributes": [attribute_result.get("attribute")]
                    }
                }
            },
            headers={'product': True}
        )
        response.status_code = attribute_result.get("status_code", 200)
        return {"message": attribute_result.get("message", [])}


@router.get("/api/v1/assignee/{name}/attrs/", tags=["assignee"], status_code=200)
def get_all_attributes_by_assignee(
        response: Response,
        name: str = Path(..., min_length=3, max_length=255)
) -> dict:
    """
    Get all the attributes of assignee collection in database.
    """
    rpc.response_len_setter(response_len=1)
    result = rpc.publish(
        message={
            "attribute": {
                "action": "get_all_attributes_by_assignee",
                "body": {
                    "name": name
                }
            }
        },
        headers={'attribute': True}
    )
    attribute_result = result.get("attribute", {})
    if not attribute_result.get("success"):
        raise HTTPException(status_code=attribute_result.get("status_code", 500),
                            detail={"error": attribute_result.get("error", "Something went wrong")})
    else:
        response.status_code = attribute_result.get("status_code", 200)
        return {"message": attribute_result.get("message", [])}


@router.delete("/api/v1/assignee/{name}/attr/{attr_name}", tags=["assignee"], status_code=200)
def delete_attribute_from_assignee(
        response: Response,
        attr_name: str = Path(..., min_length=3, max_length=255),
        name: str = Path(..., min_length=3, max_length=255)
) -> dict:
    """
    Delete an attribute from assignee collection in database.
    """
    rpc.response_len_setter(response_len=1)
    result = rpc.publish(
        message={
            "attribute": {
                "action": "delete_attribute_from_assignee",
                "body": {
                    "name": name,
                    "attr_name": attr_name
                }
            }
        },
        headers={'attribute': True}
    )
    attribute_result = result.get("attribute", {})
    if not attribute_result.get("success"):
        raise HTTPException(status_code=attribute_result.get("status_code", 500),
                            detail={"error": attribute_result.get("error", "Something went wrong")})
    else:
        response.status_code = attribute_result.get("status_code", 200)
        return {"message": attribute_result.get("message", [])}


@router.get("/api/v1/assignees/", tags=["assignee"], status_code=200)
def get_all_assignees(
        response: Response
) -> dict:
    """
    Get all the assignees(collections of the database beside main one).
    """
    rpc.response_len_setter(response_len=1)
    result = rpc.publish(
        message={
            "attribute": {
                "action": "get_all_assignees",
                "body": {}
            }
        },
        headers={'attribute': True}
    )
    assignee_result = result.get("attribute", {})
    if not assignee_result.get("success"):
        raise HTTPException(status_code=assignee_result.get("status_code", 500),
                            detail={"error": assignee_result.get("error", "Something went wrong")})
    else:
        response.status_code = assignee_result.get("status_code", 200)
        return {"message": assignee_result.get("message", [])}
