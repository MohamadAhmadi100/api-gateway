from typing import Optional

from fastapi import APIRouter, Response
from fastapi import Query, HTTPException

from source.message_broker.rabbit_server import RabbitRPC
from source.routers.gallery.validators.gallery import Gallery

router = APIRouter()


@router.get("/gallery/", status_code=200)
def get_type_api(response: Response, file_type: Optional[str] = Query(None)) -> dict:
    """
    get all types or one type
    """
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        result = rpc.publish(
            message={
                "gallery": {
                    "action": "get_type_api",
                    "body": {
                        "file_type": file_type
                    }
                }
            },
            headers={'gallery': True}
        )
        gallery_result = result.get("gallery", {})
        if gallery_result.get("success"):
            response.status_code = gallery_result.get("status_code", 200)
            return {"message": gallery_result.get("message")}
        raise HTTPException(status_code=gallery_result.get("status_code", 500),
                            detail={"error": gallery_result.get("error", "Something went wrong")})


@router.put("/gallery/", status_code=201)
def set_type_api(
        response: Response,
        item: Gallery) -> dict:
    """
    this api is used for adding or editing type of file and ...
    """
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        result = rpc.publish(
            message={
                "gallery": {
                    "action": "set_type_api",
                    "body": {
                        "item": item.dict()
                    }
                }
            },
            headers={'gallery': True}
        )
        gallery_result = result.get("gallery", {})
        if gallery_result.get("success"):
            response.status_code = gallery_result.get("status_code", 200)
            return {"message": gallery_result.get("message")}
        raise HTTPException(status_code=gallery_result.get("status_code", 500),
                            detail={"error": gallery_result.get("error", "Something went wrong")})


@router.delete("/gallery/", status_code=200)
def remove_type_api(
        response: Response,
        file_type: str) -> dict:
    """
    remove category , sub_category ,or type
    """
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        result = rpc.publish(
            message={
                "gallery": {
                    "action": "remove_type_api",
                    "body": {
                        "file_type": file_type
                    }
                }
            },
            headers={'gallery': True}
        )
        gallery_result = result.get("gallery", {})
        if gallery_result.get("success"):
            response.status_code = gallery_result.get("status_code", 200)
            return {"message": gallery_result.get("message")}
        raise HTTPException(status_code=gallery_result.get("status_code", 500),
                            detail={"error": gallery_result.get("error", "Something went wrong")})
