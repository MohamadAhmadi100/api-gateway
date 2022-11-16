from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Depends, Body, Header

from source.helpers.case_converter import convert_case
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.customer.module.auth import AuthHandler
from source.routers.mobile_app.validators.model import PredictClass, FavoriteTeam

router = APIRouter()

auth_handler = AuthHandler()


@router.post("/add_favorite_team/", tags=["FavoriteTeams"])
def add_favorite_team(
        auth_header=Depends(auth_handler.check_current_user_tokens),
        team: FavoriteTeam = Body(...),
        device_id: str = Body(..., alias="deviceId")
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
                        "team_name": team.team_name,
                        "device_id": device_id,
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
        team: FavoriteTeam = Body(...)
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
                        "team_name": team.team_name
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


# predicting match result
@router.post("/predict_match_result/", tags=["PredictMatchResult"])
def predict_match_result(
        auth_header=Depends(auth_handler.check_current_user_tokens),
        item: PredictClass = Body(...)
):
    """
    Predict match result
    """
    user, token_dict = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        predict_result = rpc.publish(
            message={
                "mobile_app": {
                    "action": "predict_match_result",
                    "body": {
                        "customer_id": user.get("user_id"),
                        "match_id": item.match_id,
                        "match_result": item.match_result,
                        "home_team_score": item.home_team_score,
                        "away_team_score": item.away_team_score
                    }
                }
            },
            headers={'mobile_app': True}
        )
        predict_result = predict_result.get("mobile_app", {})
        if predict_result.get("success"):
            return convert_case({"message": predict_result.get("message")}, 'camel')
        raise HTTPException(status_code=predict_result.get("status_code", 500),
                            detail={"error": predict_result.get("error", "Something went wrong")})


@router.post("/get_profile_data/", tags=["GetUserData"])
def get_user_profile(
        auth_header=Depends(auth_handler.check_current_user_tokens)
):
    user, token_dict = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        customer_result = rpc.publish(
            message={
                "customer": {
                    "action": "get_customer_data_by_id_league",
                    "body": {
                        "customer_id_list": [user.get("user_id")]
                    }
                }
            },
            headers={'customer': True}
        )
        customer_result = customer_result.get("customer", {})
        if not customer_result.get("success"):
            raise HTTPException(status_code=customer_result.get("status_code", 500),
                                detail={"error": customer_result.get("error", "Something went wrong")})
        customer_result = customer_result.get("message").get(str(user.get("user_id")))
        user_result = rpc.publish(
            message={
                "mobile_app": {
                    "action": "get_user_profile_data",
                    "body": {
                        "customer_id": user.get("user_id")
                    }
                }
            },
            headers={'mobile_app': True}
        )
        user_result = user_result.get("mobile_app", {})
        if user_result.get("success"):
            user_result.get("message").update(customer_result)
            return convert_case({"message": user_result.get("message")}, 'camel')
        raise HTTPException(status_code=user_result.get("status_code", 500),
                            detail={"error": user_result.get("error", "Something went wrong")})


@router.post("/get_user_rank/", tags=["GetUserData"])
def get_user_ranks(
        auth_header=Depends(auth_handler.check_current_user_tokens)
):
    user, token_dict = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        rank_result = rpc.publish(
            message={
                "mobile_app": {
                    "action": "get_user_rank",
                    "body": {
                        "customer_id": user.get("user_id")
                    }
                }
            },
            headers={'mobile_app': True}
        )
        rank_result = rank_result.get("mobile_app", {})
        if not rank_result.get("success"):
            raise HTTPException(status_code=rank_result.get("status_code", 500),
                                detail={"error": rank_result.get("error", "Something went wrong")})
        rank_result = rank_result.get("message")
        customer_result = rpc.publish(
            message={
                "customer": {
                    "action": "get_customer_data_by_id_league",
                    "body": {
                        "customer_id_list": rank_result.get("user_list")
                    }
                }
            },
            headers={'customer': True}
        )
        customer_result = customer_result.get("customer", {})
        if not customer_result.get("success"):
            raise HTTPException(status_code=customer_result.get("status_code", 500),
                                detail={"error": customer_result.get("error", "Something went wrong")})
        customer_result = customer_result.get("message", {})
        for usr in rank_result.get("five_best"):
            customer = customer_result.get(str(usr["customer_id"]))
            usr.update(customer)
        rank_result["user"].update(customer_result.get(str(rank_result["user"]["customer_id"])))
        del rank_result["user_list"]
        return convert_case({"message": rank_result}, 'camel')
