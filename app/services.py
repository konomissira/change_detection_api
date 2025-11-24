from sqlalchemy.orm import Session
from app.models import UserSnapshot, ChangeDetectionResult
from app.schemas import (
    UserSnapshotCreate,
    ChangeDetectionRequest,
    ChangeDetectionResponse,
    ChangeDetectionMetrics,
)


class SnapshotService:
    """Service class for user snapshot operations"""

    @staticmethod
    def create_snapshot(db: Session, snapshot_data: UserSnapshotCreate) -> UserSnapshot:
        """Create a new user snapshot in the database"""
        db_snapshot = UserSnapshot(
            snapshot_date=snapshot_data.snapshot_date,
            snapshot_name=snapshot_data.snapshot_name,
            user_ids=snapshot_data.user_ids,
            total_users=len(snapshot_data.user_ids),
        )
        db.add(db_snapshot)
        db.commit()
        db.refresh(db_snapshot)
        return db_snapshot

    @staticmethod
    def get_all_snapshots(db: Session) -> list[UserSnapshot]:
        """Get all user snapshots from the database"""
        return db.query(UserSnapshot).order_by(UserSnapshot.snapshot_date.desc()).all()

    @staticmethod
    def get_snapshot_by_id(db: Session, snapshot_id: int) -> UserSnapshot | None:
        """Get a specific snapshot by ID"""
        return db.query(UserSnapshot).filter(UserSnapshot.id == snapshot_id).first()

    @staticmethod
    def get_snapshot_by_name(db: Session, snapshot_name: str) -> UserSnapshot | None:
        """Get a specific snapshot by name"""
        return (
            db.query(UserSnapshot)
            .filter(UserSnapshot.snapshot_name == snapshot_name)
            .first()
        )

    @staticmethod
    def delete_snapshot(db: Session, snapshot_id: int) -> bool:
        """Delete a snapshot by ID"""
        snapshot = SnapshotService.get_snapshot_by_id(db, snapshot_id)
        if snapshot:
            db.delete(snapshot)
            db.commit()
            return True
        return False


class ChangeDetectionService:
    """Service class for change detection operations using SET operations"""

    @staticmethod
    def detect_changes(
        db: Session, request: ChangeDetectionRequest
    ) -> ChangeDetectionResponse:
        """
        Detect changes between two user snapshots using SET operations.

        SET OPERATIONS:
        - NEW USERS: snapshot_2 - snapshot_1 (SET DIFFERENCE)
        - CHURNED USERS: snapshot_1 - snapshot_2 (SET DIFFERENCE)
        - RETAINED USERS: snapshot_1 & snapshot_2 (SET INTERSECTION)
        """
        # Get both snapshots
        snapshot_1 = SnapshotService.get_snapshot_by_id(db, request.snapshot_1_id)
        snapshot_2 = SnapshotService.get_snapshot_by_id(db, request.snapshot_2_id)

        if not snapshot_1:
            raise ValueError(f"Snapshot with id {request.snapshot_1_id} not found")
        if not snapshot_2:
            raise ValueError(f"Snapshot with id {request.snapshot_2_id} not found")

        # Convert user_ids lists to SETS for efficient operations
        users_snapshot_1 = set(snapshot_1.user_ids)
        users_snapshot_2 = set(snapshot_2.user_ids)

        # ============================================
        # SET OPERATIONS - The core of change detection!
        # ============================================

        # SET DIFFERENCE: Users in snapshot_2 but NOT in snapshot_1 = NEW USERS
        new_users = users_snapshot_2 - users_snapshot_1

        # SET DIFFERENCE: Users in snapshot_1 but NOT in snapshot_2 = CHURNED USERS
        churned_users = users_snapshot_1 - users_snapshot_2

        # SET INTERSECTION: Users in BOTH snapshots = RETAINED USERS
        retained_users = users_snapshot_1 & users_snapshot_2

        # ============================================
        # Calculate metrics
        # ============================================
        new_users_count = len(new_users)
        churned_users_count = len(churned_users)
        retained_users_count = len(retained_users)

        # Growth rate: (new - churned) / snapshot_1 total * 100
        if snapshot_1.total_users > 0:
            growth_rate = round(
                ((new_users_count - churned_users_count) / snapshot_1.total_users) * 100,
                2,
            )
        else:
            growth_rate = 0.0

        # Churn rate: churned / snapshot_1 total * 100
        if snapshot_1.total_users > 0:
            churn_rate = round(
                (churned_users_count / snapshot_1.total_users) * 100, 2
            )
        else:
            churn_rate = 0.0

        # Retention rate: retained / snapshot_1 total * 100
        if snapshot_1.total_users > 0:
            retention_rate = round(
                (retained_users_count / snapshot_1.total_users) * 100, 2
            )
        else:
            retention_rate = 0.0

        # Create and save the result
        db_result = ChangeDetectionResult(
            comparison_name=request.comparison_name,
            snapshot_1_id=snapshot_1.id,
            snapshot_2_id=snapshot_2.id,
            snapshot_1_date=snapshot_1.snapshot_date,
            snapshot_2_date=snapshot_2.snapshot_date,
            new_users=list(new_users),
            churned_users=list(churned_users),
            retained_users=list(retained_users),
            new_users_count=new_users_count,
            churned_users_count=churned_users_count,
            retained_users_count=retained_users_count,
            growth_rate=growth_rate,
            churn_rate=churn_rate,
            retention_rate=retention_rate,
        )
        db.add(db_result)
        db.commit()
        db.refresh(db_result)

        # Return formatted response
        return ChangeDetectionResponse(
            id=db_result.id,
            comparison_name=db_result.comparison_name,
            snapshot_1_id=db_result.snapshot_1_id,
            snapshot_2_id=db_result.snapshot_2_id,
            snapshot_1_date=db_result.snapshot_1_date,
            snapshot_2_date=db_result.snapshot_2_date,
            new_users=db_result.new_users,
            churned_users=db_result.churned_users,
            retained_users=db_result.retained_users,
            metrics=ChangeDetectionMetrics(
                new_users_count=db_result.new_users_count,
                churned_users_count=db_result.churned_users_count,
                retained_users_count=db_result.retained_users_count,
                growth_rate=db_result.growth_rate,
                churn_rate=db_result.churn_rate,
                retention_rate=db_result.retention_rate,
            ),
            created_at=db_result.created_at,
        )

    @staticmethod
    def get_all_results(db: Session) -> list[ChangeDetectionResponse]:
        """Get all change detection results from the database"""
        results = (
            db.query(ChangeDetectionResult)
            .order_by(ChangeDetectionResult.created_at.desc())
            .all()
        )
        return [
            ChangeDetectionResponse(
                id=r.id,
                comparison_name=r.comparison_name,
                snapshot_1_id=r.snapshot_1_id,
                snapshot_2_id=r.snapshot_2_id,
                snapshot_1_date=r.snapshot_1_date,
                snapshot_2_date=r.snapshot_2_date,
                new_users=r.new_users,
                churned_users=r.churned_users,
                retained_users=r.retained_users,
                metrics=ChangeDetectionMetrics(
                    new_users_count=r.new_users_count,
                    churned_users_count=r.churned_users_count,
                    retained_users_count=r.retained_users_count,
                    growth_rate=r.growth_rate,
                    churn_rate=r.churn_rate,
                    retention_rate=r.retention_rate,
                ),
                created_at=r.created_at,
            )
            for r in results
        ]

    @staticmethod
    def get_result_by_id(db: Session, result_id: int) -> ChangeDetectionResponse | None:
        """Get a specific change detection result by ID"""
        result = (
            db.query(ChangeDetectionResult)
            .filter(ChangeDetectionResult.id == result_id)
            .first()
        )
        if not result:
            return None

        return ChangeDetectionResponse(
            id=result.id,
            comparison_name=result.comparison_name,
            snapshot_1_id=result.snapshot_1_id,
            snapshot_2_id=result.snapshot_2_id,
            snapshot_1_date=result.snapshot_1_date,
            snapshot_2_date=result.snapshot_2_date,
            new_users=result.new_users,
            churned_users=result.churned_users,
            retained_users=result.retained_users,
            metrics=ChangeDetectionMetrics(
                new_users_count=result.new_users_count,
                churned_users_count=result.churned_users_count,
                retained_users_count=result.retained_users_count,
                growth_rate=result.growth_rate,
                churn_rate=result.churn_rate,
                retention_rate=result.retention_rate,
            ),
            created_at=result.created_at,
        )

    @staticmethod
    def delete_result(db: Session, result_id: int) -> bool:
        """Delete a change detection result by ID"""
        result = (
            db.query(ChangeDetectionResult)
            .filter(ChangeDetectionResult.id == result_id)
            .first()
        )
        if result:
            db.delete(result)
            db.commit()
            return True
        return False
