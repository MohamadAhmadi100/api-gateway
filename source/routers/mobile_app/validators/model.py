from typing import Optional

from pydantic import BaseModel
from enum import Enum


class ForceUpdate(BaseModel):
    build_number: int
    build_name: str
    os_type: str
    force_update: bool
    link_download: str

    class Config:
        schema_extra = {
            "example": {
                "build_number": 1,
                "build_name": "1.0.0",
                "os_type": "android",
                "force_update": True,
                "link_download": "https://google.com"
            }
        }


class MatchResult(str, Enum):
    Win = "Win"
    Loss = "loss"
    Draw = "Draw"


class PredictClass(BaseModel):
    game_id: int
    match_result: MatchResult
    home_team_score: Optional[int] = None
    away_team_score: Optional[int] = None

    class Config:
        schema_extra = {
            "example": {
                "game_id": 1,
                "match_result": "Draw",
                "home_team_score": 1,
                "away_team_score": 1
            }
        }
