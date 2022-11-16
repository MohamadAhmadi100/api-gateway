from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Depends, Body, Header

from source.helpers.case_converter import convert_case
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.customer.module.auth import AuthHandler
from source.routers.mobile_app.validators.model import PredictClass, FavoriteTeam

router = APIRouter()

auth_handler = AuthHandler()


@router.get("/get_wcup_table", tags=["Football"])
def get_world_cup_table(
        auth_header=Depends(auth_handler.check_current_user_tokens)
):
    """
    Get world cup table
    """
    user, token_dict = auth_header

    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        product_result = rpc.publish(
            message={
                "mobile_app": {
                    "action": "get_world_cup_league_table",
                    "body": {
                        "user_id": user.get("user_id")
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


@router.get("/update_wcup_groups_list", tags=["Football"])
def update_world_cup_groups_list():
    """
    Get weeks list
    """
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        product_result = rpc.publish(
            message={
                "mobile_app": {
                    "action": "update_world_cup_groups_list",
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


@router.get("/get_wcup_group_matches/", tags=["Football"])
def get_world_cup_group_matches(
        group: Optional[str] = Query(
            None, regexPattern=r"^([abcdefghABCDEFGH]{1})"
        )
):
    """
    Get week matches
    """
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        product_result = rpc.publish(
            message={
                "mobile_app": {
                    "action": "get_world_cup_group_matches",
                    "body": {
                        "group": group
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


@router.get("/get_wcup_favorite_teams/", tags=["FavoriteTeams"])
def get_world_cup_favorite_teams(auth_header=Depends(auth_handler.check_current_user_tokens)):
    """
    Get favorite teams
    """
    user, token_dict = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        product_result = rpc.publish(
            message={
                "mobile_app": {
                    "action": "get_world_cup_favorite_teams",
                    "body": {
                        "customer_id": user.get("user_id")
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


@router.get("/get_today_wcup_matches", tags=["Football"])
def get_today_world_cup_matches():
    """
    Get league table
    """

    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        product_result = rpc.publish(
            message={
                "mobile_app": {
                    "action": "get_today_world_cup_matches",
                    "body": {
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
