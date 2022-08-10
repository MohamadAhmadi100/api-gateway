from fastapi import HTTPException, APIRouter, Response, Path

from source.helpers.case_converter import convert_case
from source.helpers.rabbit_config import new_rpc
# from source.message_broker.rabbit_server import RabbitRPC
from source.routers.customer.module.auth import AuthHandler
from source.routers.product.validators.kowsar import KowsarConfig, KowsarGroup, KowsarPart

router = APIRouter()

auth_handler = AuthHandler()


@router.post("/kowsar/static/", tags=["Kowsar"])
def create_kowsar_static_configs(item: KowsarConfig):
    """
    Create a new kowsar group
    """
    product_result = new_rpc.publish(
        message=[{
            "product": {
                "action": "create_kowsar_static_configs",
                "body": {
                    "config_type": item.config_type,
                    "system_code": item.system_code,
                    "name": item.name,
                }
            }
        }]
    )
    if product_result.get("success"):
        return convert_case({"message": product_result.get("message")}, 'camel')
    raise HTTPException(status_code=product_result.get("status_code", 500),
                        detail={"error": product_result.get("error", "Something went wrong")})


# get kowsar static configs by config_type
@router.get("/kowsar/static/{config_type}/", tags=["Kowsar"])
def get_kowsar_static_configs_by_config_type(config_type: str):
    """
    Get kowsar static configs by config_type
    """
    product_result = new_rpc.publish(
        message=[{
            "product": {
                "action": "get_kowsar_static_configs_by_config_type",
                "body": {
                    "config_type": config_type,
                }
            }
        }]
    )
    if product_result.get("success"):
        return convert_case(product_result.get("message"), 'camel')
    raise HTTPException(status_code=product_result.get("status_code", 500),
                        detail={"error": product_result.get("error", "Something went wrong")})


@router.post("/kowsar/create_kowsar_group/", tags=["Kowsar"])
def create_kowsar_group(
        response: Response,
        item: KowsarGroup
):
    """
    Create kowsar group
    """
    product_result = new_rpc.publish(
        message=[{
            "product": {
                "action": "create_kowsar_group",
                "body": {
                    "system_code": item.system_code,
                    "name": item.name,
                    "parent_system_code": item.parent_system_code,
                    "configs": item.configs
                }
            }
        }]
    )
    if product_result.get("success"):
        response.status_code = product_result.get("status_code", 200)
        return convert_case(product_result.get("message"), 'camel')
    raise HTTPException(status_code=product_result.get("status_code", 500),
                        detail={"error": product_result.get("error", "Something went wrong")})


@router.post("/kowsar/create_system_code/", tags=["Kowsar"])
def create_system_code(
        response: Response,
        item: KowsarPart
):
    """
    Create kowsar system code
    """
    product_result = new_rpc.publish(
        message=[{
            "product": {
                "action": "create_system_code",
                "body": {
                    "system_code": item.system_code,
                    "storage_ids": item.storage_ids,
                    "parent_system_code": item.parent_system_code,
                    "guaranty": item.guaranty
                }
            }
        }]
    )
    if product_result.get("success"):
        response.status_code = product_result.get("status_code", 200)
        return convert_case(product_result.get("message"), 'camel')
    raise HTTPException(status_code=product_result.get("status_code", 500),
                        detail={"error": product_result.get("error", "Something went wrong")})


@router.get("/kowsar/items/{systemCode}/", tags=["Kowsar"])
def get_kowsar_items(
        response: Response,
        system_code: str = Path(..., min_length=2, max_length=16, alias='systemCode')
):
    """
    Get children of kowsar item
    """
    product_result = new_rpc.publish(
        message=[
            {
                "product": {
                    "action": "get_kowsar_items",
                    "body": {
                        "system_code": system_code
                    }
                }
            }
        ]
    )
    if product_result.get("success"):
        response.status_code = product_result.get("status_code", 200)
        return convert_case(product_result.get("message"), 'camel')
    raise HTTPException(status_code=product_result.get("status_code", 500),
                        detail={"error": product_result.get("error", "Something went wrong")})
