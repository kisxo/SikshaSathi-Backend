from pydantic import BaseModel, Field

class DailyTrackingItem(BaseModel):
    activity: str
    value: bool

class DailyTrackingCreate(BaseModel):
    daily_tracking_data: list[DailyTrackingItem]