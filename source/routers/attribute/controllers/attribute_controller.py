from typing import Optional

from fastapi import Query, Path, HTTPException, APIRouter, Response

from source.message_broker.rabbit_server import RabbitRPC
from source.routers.attribute.validators.attributes import Attribute

from source.helpers.case_converter import convert_case

router = APIRouter()

# initialize rabbit mq
rpc = RabbitRPC(exchange_name='headers_exchange', timeout=5)
rpc.connect()
rpc.consume()


@router.get("/", status_code=200)
def main_page(
        response: Response,
        page: Optional[int] = Query(1, ge=1, le=1000)
) -> list:
    """
    Get all the attributes in main collection in database.
    It shows 10 attributes per page.
    """
    rpc.response_len_setter(response_len=1)
    result = rpc.publish(
        message={
            "attribute": {
                "action": "main_page",
                "body": {
                    "page": page
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
        return convert_case(attribute_result.get("message", []), "camel")


@router.post("/attr/", tags=["attribute"], status_code=201)
def add_attribute(
        response: Response,
        item: Attribute
) -> dict:
    """
    Add an attribute to main collection in database with this information:
    - **name**: name of the attribute(for searching)
    - **label**: label of the attribute(for display)
    - **input_type**: type of input for the attribute
        - It will be index number of these things: ['Text Field', 'Text Area', 'Text Editor', 'Date', 'Date and Time',
        'Yes or No', 'Multiple Select', 'Dropdown', 'Price', 'Media Image', 'Color', 'Number']
    - **required**: if the attribute is required or not(Boolean type)
    - **use_in_filter**: if the attribute is used in filter or notThe
    - **use_for_sort**: if the attribute is used for sorting or not(Boolean type)
    - **parent**: declare parent attribute to set attribute to it's children
    - **default_value**: default value of the attribute
    - **values**: list of values for the attribute
    - **set_to_nodes**: if the attribute is set to nodes or not(Boolean type)
    """
    rpc.response_len_setter(response_len=1)
    result = rpc.publish(
        message={
            "attribute": {
                "action": "add_attribute",
                "body": {
                    "item": item.dict()
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


@router.get("/attrs/{page}", tags=["attribute"], status_code=200)
def get_attributes(
        response: Response,
        page: int = Path(1, ge=1, le=1000),
        per_page: int = Query(10, ge=1, le=1000)
) -> dict:
    """
    Get all the attributes of the main collection in database.
    It shows 10 attributes per page.
    """
    rpc.response_len_setter(response_len=1)
    result = rpc.publish(
        message={
            "attribute": {
                "action": "get_attributes",
                "body": {
                    "page": page,
                    "per_page": per_page
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
        return {"message": convert_case(attribute_result.get("message", []), "camel")}


@router.get("/attr/{attribute_name}", tags=["attribute"], status_code=200)
def get_attribute_by_name(
        response: Response,
        attribute_name: str = Path(..., min_length=3, max_length=255)
) -> dict:
    """
    Get an attribute by name in main collection in database.
    """
    rpc.response_len_setter(response_len=1)
    result = rpc.publish(
        message={
            "attribute": {
                "action": "get_attribute_by_name",
                "body": {
                    "attribute_name": attribute_name
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
        return {"message": convert_case(attribute_result.get("message", []), "camel")}


@router.put("/attr/", tags=["attribute"], status_code=202)
def update_attribute(
        response: Response,
        item: Attribute,
) -> dict:
    """
    Update an attribute by name in main collection in database.
    """
    rpc.response_len_setter(response_len=1)
    result = rpc.publish(
        message={
            "attribute": {
                "action": "update_attribute",
                "body": {
                    "item": item.dict(),
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


@router.delete("/attr/{attribute_name}", tags=["attribute"], status_code=200)
def delete_attribute(
        response: Response,
        attribute_name: str = Path(..., min_length=3, max_length=255)
) -> dict:
    """
    Delete an attribute by name in main collection in database.
    """
    rpc.response_len_setter(response_len=1)
    result = rpc.publish(
        message={
            "attribute": {
                "action": "delete_attribute",
                "body": {
                    "attribute_name": attribute_name
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
