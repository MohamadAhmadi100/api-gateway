from enum import Enum
from typing import Optional

from fastapi import Body
from fastapi import HTTPException
from pydantic import BaseModel, validator
from threading import Timer

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
    Home = "Home"
    Away = "Away"
    Draw = "Draw"


class PredictClass(BaseModel):
    match_id: int = Body(..., alias="matchId")
    match_result: MatchResult = Body(..., alias="matchResult")
    home_team_score: Optional[str] = Body(default=None, alias="homeTeamScore")
    away_team_score: Optional[str] = Body(default=None, alias="awayTeamScore")


class FavoriteTeam(BaseModel):
    team_name: str = Body(..., alias="teamName")

    @validator('team_name')
    def check_team_name(cls, v):
        if not isinstance(v, str):
            raise HTTPException(status_code=400, detail="team_name must be a string")
        return v
