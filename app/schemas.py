from datetime import datetime
from pydantic import BaseModel


class WeeklyMemoryCreate(BaseModel):
    text: str


class WeeklyMemoryOut(BaseModel):
    week_monday: datetime
    text: str
    author: str
    # Pydantic v2 configuration: use attributes from ORM objects
    model_config = {"from_attributes": True}


class GoalCreate(BaseModel):
    text: str


class GoalOut(BaseModel):
    id: int
    text: str
    author: str
    created_at: datetime
    model_config = {"from_attributes": True}


class UnlinkedCreate(BaseModel):
    text: str


class UnlinkedOut(BaseModel):
    id: int
    text: str
    author: str
    created_at: datetime
    model_config = {"from_attributes": True}
