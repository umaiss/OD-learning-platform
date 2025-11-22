from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, List
from datetime import date
from db.database import get_db
from db.models import Learner, DailyMission
from agents.missions import MissionGenerator, DailyMissionsOutput
import json

router = APIRouter(prefix="/missions", tags=["missions"])
mission_generator = MissionGenerator()


class GenerateDailyMissionsRequest(BaseModel):
    learner_id: int
    skill_map: Dict[str, str]


class GenerateDailyMissionsResponse(BaseModel):
    learner_id: int
    mission_id: int
    missions: List[str]
    xp: int
    streak_increment: int
    date: str
    message: str = "Daily missions generated successfully"


@router.post("/daily", response_model=GenerateDailyMissionsResponse, status_code=status.HTTP_201_CREATED)
async def generate_daily_missions(
    request: GenerateDailyMissionsRequest,
    db: Session = Depends(get_db)
):
    """Generate daily missions for a learner"""
    try:
        # Verify learner exists
        learner = db.query(Learner).filter(Learner.id == request.learner_id).first()
        if not learner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Learner with id {request.learner_id} not found"
            )
        
        # Call the agent
        result: DailyMissionsOutput = await mission_generator.generate_daily_missions(
            skill_map=request.skill_map
        )
        
        # Check if mission already exists for today
        today = date.today()
        existing_mission = db.query(DailyMission).filter(
            DailyMission.learner_id == request.learner_id,
            DailyMission.date == today
        ).first()
        
        if existing_mission:
            # Update existing mission
            existing_mission.missions_json = result.missions
            existing_mission.xp = result.xp
            existing_mission.streak = existing_mission.streak + result.streak_increment
            db.commit()
            db.refresh(existing_mission)
            mission_id = existing_mission.id
        else:
            # Create new mission
            daily_mission = DailyMission(
                learner_id=request.learner_id,
                missions_json=result.missions,
                xp=result.xp,
                streak=result.streak_increment,
                date=today
            )
            db.add(daily_mission)
            db.commit()
            db.refresh(daily_mission)
            mission_id = daily_mission.id
        
        return GenerateDailyMissionsResponse(
            learner_id=request.learner_id,
            mission_id=mission_id,
            missions=result.missions,
            xp=result.xp,
            streak_increment=result.streak_increment,
            date=str(today)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating daily missions: {str(e)}"
        )

