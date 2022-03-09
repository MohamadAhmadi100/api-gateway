import json
from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi import File, Response

from source.message_broker.rabbit_server import RabbitRPC

router = APIRouter()

# initialize rabbit mq
rpc = RabbitRPC(exchange_name='headers_exchange', timeout=5)
rpc.connect()
rpc.consume()


@router.put("/gallery/file/", status_code=201)
def set_files_api(response: Response, file_type: str, path: str, file_id: Optional[int] = None,
                  name: Optional[str] = None,
                  request_body: bytes = File(...)) -> dict:
    """
    this api is used for adding or editing files
    """
    rpc.response_len_setter(response_len=1)
    result = rpc.publish(
        message=request_body,
        headers={'gallery': True},
        extra_data=json.dumps({
            "gallery": {
                "action": "set_files_api",
                "body": {
                    "file_type": file_type,
                    "path": path,
                    "file_id": file_id,
                    "name": name,
                }
            }
        })
    )
    gallery_result = result.get("gallery", {})
    if gallery_result.get("success"):
        response.status_code = gallery_result.get("status_code", 200)
        return {"message": gallery_result.get("message")}
    raise HTTPException(status_code=gallery_result.get("status_code", 500),
                        detail={"error": gallery_result.get("error", "Something went wrong")})


@router.delete("/gallery/file/", status_code=200)
def remove_files_api(
        response: Response,
        file_name: str, path: str) -> dict:
    """
    remove category , sub_category ,or type
    """
    rpc.response_len_setter(response_len=1)
    result = rpc.publish(
        message={
            "gallery": {
                "action": "remove_files_api",
                "body": {
                    "file_name": file_name,
                    "path": path
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


@router.get("/gallery/file/", status_code=200)
def get_file_api(
        response: Response,
        file_name: str, path: str) -> dict:
    """
    get file link(s)
    """
    rpc.response_len_setter(response_len=1)
    result = rpc.publish(
        message={
            "gallery": {
                "action": "get_file_api",
                "body": {
                    "file_name": file_name,
                    "path": path
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
