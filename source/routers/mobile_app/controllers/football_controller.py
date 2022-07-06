from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Depends, Body

from source.helpers.case_converter import convert_case
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.customer.module.auth import AuthHandler

router = APIRouter()

auth_handler = AuthHandler()


@router.get("/get_league_table", tags=["Football"])
def get_league_table(
):
    """
    Get league table
    """
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        product_result = rpc.publish(
            message={
                "mobile_app": {
                    "action": "get_league_table",
                    "body": {}
                }
            },
            headers={'mobile_app': True}
        )
        product_result = product_result.get("mobile_app", {})
        if product_result.get("success"):
            return convert_case({"message": product_result.get("message")}, 'camel')
        raise HTTPException(status_code=product_result.get("status_code", 500),
                            detail={"error": product_result.get("error", "Something went wrong")})


@router.get("/update_weeks_list", tags=["Football"])
def update_weeks_list():
    """
    Get weeks list
    """
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        product_result = rpc.publish(
            message={
                "mobile_app": {
                    "action": "update_weeks_list",
                    "body": {}
                }
            },
            headers={'mobile_app': True}
        )
        product_result = product_result.get("mobile_app", {})
        if product_result.get("success"):
            return convert_case({"message": product_result.get("message")}, 'camel')
        raise HTTPException(status_code=product_result.get("status_code", 500),
                            detail={"error": product_result.get("error", "Something went wrong")})


@router.get("/get_week_matches/", tags=["Football"])
def get_week_matches(
        week: Optional[int] = Query(None)
):
    """
    Get week matches
    """
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        product_result = rpc.publish(
            message={
                "mobile_app": {
                    "action": "get_week_matches",
                    "body": {
                        "week": week
                    }
                }
            },
            headers={'mobile_app': True}
        )
        product_result = product_result.get("mobile_app", {})
        if product_result.get("success"):
            return convert_case({"message": product_result.get("message")}, 'camel')
        raise HTTPException(status_code=product_result.get("status_code", 500),
                            detail={"error": product_result.get("error", "Something went wrong")})


@router.get("/get_favorite_teams/", tags=["FavoriteTeams"])
def get_favorite_teams(auth_header=Depends(auth_handler.check_current_user_tokens)):
    """
    Get favorite teams
    """
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        product_result = rpc.publish(
            message={
                "mobile_app": {
                    "action": "get_favorite_teams",
                    "body": {
                        "customer_id": auth_header.user_id
                    }
                }
            },
            headers={'mobile_app': True}
        )
        product_result = product_result.get("mobile_app", {})
        if product_result.get("success"):
            return convert_case({"message": product_result.get("message")}, 'camel')
        raise HTTPException(status_code=product_result.get("status_code", 500),
                            detail={"error": product_result.get("error", "Something went wrong")})


@router.post("/add_favorite_team/", tags=["FavoriteTeams"])
def add_favorite_team(
        auth_header=Depends(auth_handler.check_current_user_tokens),
        team_name: str = Body(...)
):
    """
    Add favorite team
    """
    user, token_dict = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        product_result = rpc.publish(
            message={
                "mobile_app": {
                    "action": "add_favorite_team",
                    "body": {
                        "customer_id": user.get("user_id"),
                        "team_name": team_name
                    }
                }
            },
            headers={'mobile_app': True}
        )
        product_result = product_result.get("mobile_app", {})
        if product_result.get("success"):
            return convert_case({"message": product_result.get("message")}, 'camel')
        raise HTTPException(status_code=product_result.get("status_code", 500),
                            detail={"error": product_result.get("error", "Something went wrong")})


@router.delete("/remove_favorite_team/", tags=["FavoriteTeams"])
def remove_favorite_team(
        auth_header=Depends(auth_handler.check_current_user_tokens),
        team_name: str = Body(...)
):
    """
    Remove favorite team
    """
    user, token_dict = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        product_result = rpc.publish(
            message={
                "mobile_app": {
                    "action": "remove_favorite_team",
                    "body": {
                        "customer_id": user.get("user_id"),
                        "team_name": team_name
                    }
                }
            },
            headers={'mobile_app': True}
        )
        product_result = product_result.get("mobile_app", {})
        if product_result.get("success"):
            return convert_case({"message": product_result.get("message")}, 'camel')
        raise HTTPException(status_code=product_result.get("status_code", 500),
                            detail={"error": product_result.get("error", "Something went wrong")})


@router.put("/update_favorite_team/", tags=["FavoriteTeams"])
def update_favorite_team(
        auth_header=Depends(auth_handler.check_current_user_tokens),
        team_name: str = Body(...),
        new_team_name: str = Body(...)
):
    """
    Update favorite team
    """
    user, token_dict = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        product_result = rpc.publish(
            message={
                "mobile_app": {
                    "action": "update_favorite_team",
                    "body": {
                        "customer_id": user.get("user_id"),
                        "team_name": team_name,
                        "new_team_name": new_team_name
                    }
                }
            },
            headers={'mobile_app': True}
        )
        product_result = product_result.get("mobile_app", {})
        if product_result.get("success"):
            return convert_case({"message": product_result.get("message")}, 'camel')
        raise HTTPException(status_code=product_result.get("status_code", 500),
                            detail={"error": product_result.get("error", "Something went wrong")})
