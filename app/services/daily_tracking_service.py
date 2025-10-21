from app.db.models.daily_tracking_model import DailyTracking
from app.db.session import SessionDep
from fastapi import HTTPException
from sqlalchemy import select


def list_daily_tracking_by_center(center_id: int, session: SessionDep):
    try:
        statement = select(DailyTracking).where(DailyTracking.daily_tracking_center_id == center_id)
        result =  session.execute(statement).mappings().all()
        daily_trackings = []
        for row in result:
            daily_trackings.append(row.DailyTracking.__dict__)

        return daily_trackings
    except Exception as e:
        print(e)

def list_daily_tracking(session: SessionDep):
    try:
        statement = select(DailyTracking)
        result =  session.execute(statement).mappings().all()
        daily_trackings = []
        for row in result:
            daily_trackings.append(row.DailyTracking.__dict__)

        return daily_trackings
    except Exception as e:
        print(e)