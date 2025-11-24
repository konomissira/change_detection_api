from datetime import datetime
from typing import List
from pydantic import BaseModel, Field


# User Snapshot Schemas
class UserSnapshotCreate(BaseModel):
    """Schema for creating a new user snapshot"""

    snapshot_date: datetime = Field(..., description="Date/time of the snapshot")
    snapshot_name: str = Field(..., description="Name/label for the snapshot")
    user_ids: List[int] = Field(..., description="List of user IDs in this snapshot")


class UserSnapshotResponse(BaseModel):
    """Schema for user snapshot response"""

    id: int
    snapshot_date: datetime
    snapshot_name: str
    user_ids: List[int]
    total_users: int
    created_at: datetime

    class Config:
        from_attributes = True


# Change Detection Schemas
class ChangeDetectionRequest(BaseModel):
    """Schema for requesting change detection between two snapshots"""

    comparison_name: str = Field(..., description="Name for this comparison")
    snapshot_1_id: int = Field(..., description="ID of the first snapshot (earlier)")
    snapshot_2_id: int = Field(..., description="ID of the second snapshot (later)")


class ChangeDetectionMetrics(BaseModel):
    """Schema for change detection metrics"""

    new_users_count: int
    churned_users_count: int
    retained_users_count: int
    growth_rate: float
    churn_rate: float
    retention_rate: float


class ChangeDetectionResponse(BaseModel):
    """Schema for change detection response"""

    id: int
    comparison_name: str
    snapshot_1_id: int
    snapshot_2_id: int
    snapshot_1_date: datetime
    snapshot_2_date: datetime
    new_users: List[int]
    churned_users: List[int]
    retained_users: List[int]
    metrics: ChangeDetectionMetrics
    created_at: datetime

    class Config:
        from_attributes = True


# Helper response schemas
class MessageResponse(BaseModel):
    """Generic message response"""

    message: str
    details: dict | None = None


class HealthCheckResponse(BaseModel):
    """Health check response"""

    status: str
    message: str