from sqlalchemy import Column, Integer, String, DateTime, Float, JSON
from sqlalchemy.sql import func
from app.database import Base


class UserSnapshot(Base):
    """Model for storing user snapshots at different points in time"""

    __tablename__ = "user_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    snapshot_date = Column(DateTime(timezone=True), nullable=False, index=True)
    snapshot_name = Column(String, nullable=False, index=True)
    user_ids = Column(JSON, nullable=False)  # Store list of user IDs as JSON
    total_users = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<UserSnapshot(id={self.id}, name='{self.snapshot_name}', date={self.snapshot_date}, users={self.total_users})>"


class ChangeDetectionResult(Base):
    """Model for storing change detection analysis results"""

    __tablename__ = "change_detection_results"

    id = Column(Integer, primary_key=True, index=True)
    comparison_name = Column(String, nullable=False, index=True)
    snapshot_1_id = Column(Integer, nullable=False)
    snapshot_2_id = Column(Integer, nullable=False)
    snapshot_1_date = Column(DateTime(timezone=True), nullable=False)
    snapshot_2_date = Column(DateTime(timezone=True), nullable=False)

    # Results
    new_users = Column(JSON, nullable=False)  # Users in snapshot 2 but not in 1
    churned_users = Column(JSON, nullable=False)  # Users in snapshot 1 but not in 2
    retained_users = Column(JSON, nullable=False)  # Users in both snapshots

    # Metrics
    new_users_count = Column(Integer, nullable=False)
    churned_users_count = Column(Integer, nullable=False)
    retained_users_count = Column(Integer, nullable=False)
    growth_rate = Column(Float, nullable=False)
    churn_rate = Column(Float, nullable=False)
    retention_rate = Column(Float, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<ChangeDetectionResult(id={self.id}, name='{self.comparison_name}', new={self.new_users_count}, churned={self.churned_users_count}, retained={self.retained_users_count})>"