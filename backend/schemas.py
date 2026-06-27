from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    notification_email: EmailStr | None = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    notification_email: EmailStr | None
    is_active: bool
    created_at: datetime


class TargetCreate(BaseModel):
    name: str
    url: str


class TargetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    name: str
    url: str
    is_active: bool
    created_at: datetime


class CheckOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    target_id: int
    status_code: int | None
    latency_ms: float | None
    is_up: bool
    checked_at: datetime


class StatsOut(BaseModel):
    uptime_percent_24h: float
    avg_latency_24h: float | None
    uptime_percent_7d: float
    total_checks: int
