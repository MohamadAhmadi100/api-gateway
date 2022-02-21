from fastapi import APIRouter, Response, HTTPException

from source.message_broker.rabbit_server import RabbitRPC

router = APIRouter()

# initialize rabbit mq
rpc = RabbitRPC(exchange_name='headers_exchange', timeout=5)
rpc.connect()
rpc.consume()


@router.get("/gallery/dirs/", status_code=200)
def get_directories_tree(response: Response) -> dict:
    """
    geting directories and files in a path
    """
    rpc.response_len_setter(response_len=1)
    result = rpc.publish(
        message={
            "gallery": {
                "action": "get_directories_tree",
                "body": {}
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


@router.post("/gallery/dirs/{folderpath:path}", status_code=201)
def create_folder(folderpath: str, response: Response):
    """
    creating a folder by given path
    """
    rpc.response_len_setter(response_len=1)
    result = rpc.publish(
        message={
            "gallery": {
                "action": "create_folder",
                "body": {
                    "folderpath": folderpath
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


@router.delete("/gallery/dirs/{folderpath:path}", status_code=200)
def delete_folder(folderpath: str):
    """
    deleting a folder by given path
    """
    rpc.response_len_setter(response_len=1)
    result = rpc.publish(
        message={
            "gallery": {
                "action": "delete_folder",
                "body": {
                    "folderpath": folderpath
                }
            }
        },
        headers={'gallery': True}
    )
    gallery_result = result.get("gallery", {})
    if gallery_result.get("success"):
        return {"message": gallery_result.get("message")}
    raise HTTPException(status_code=gallery_result.get("status_code", 500),
                        detail={"error": gallery_result.get("error", "Something went wrong")})