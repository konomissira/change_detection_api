from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas import (
    UserSnapshotCreate,
    UserSnapshotResponse,
    ChangeDetectionRequest,
    ChangeDetectionResponse,
    ChangeDetectionMetrics,
    MessageResponse,
)
from app.services import SnapshotService, ChangeDetectionService

router = APIRouter(prefix="/api/v1", tags=["change-detection"])


# ============================================
# USER SNAPSHOT ENDPOINTS
# ============================================


@router.post(
    "/snapshots",
    response_model=UserSnapshotResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_snapshot(
    snapshot_data: UserSnapshotCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new user snapshot with a list of user IDs.

    **Example:**
    - snapshot_name: "Daily Active Users - Monday"
    - snapshot_date: "2024-01-15T00:00:00Z"
    - user_ids: [101, 102, 103, 104, 105]
    """
    # Check if snapshot name already exists
    existing = SnapshotService.get_snapshot_by_name(db, snapshot_data.snapshot_name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Snapshot with name '{snapshot_data.snapshot_name}' already exists",
        )

    try:
        new_snapshot = SnapshotService.create_snapshot(db, snapshot_data)
        return new_snapshot
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create snapshot: {str(e)}",
        )


@router.get("/snapshots", response_model=List[UserSnapshotResponse])
def get_all_snapshots(db: Session = Depends(get_db)):
    """
    Get all user snapshots.

    Returns snapshots sorted by date (most recent first).
    """
    snapshots = SnapshotService.get_all_snapshots(db)
    return snapshots


@router.get("/snapshots/{snapshot_id}", response_model=UserSnapshotResponse)
def get_snapshot(
    snapshot_id: int,
    db: Session = Depends(get_db),
):
    """
    Get a specific user snapshot by ID.
    """
    snapshot = SnapshotService.get_snapshot_by_id(db, snapshot_id)
    if not snapshot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Snapshot with id {snapshot_id} not found",
        )
    return snapshot


@router.delete("/snapshots/{snapshot_id}", response_model=MessageResponse)
def delete_snapshot(
    snapshot_id: int,
    db: Session = Depends(get_db),
):
    """
    Delete a user snapshot by ID.
    """
    deleted = SnapshotService.delete_snapshot(db, snapshot_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Snapshot with id {snapshot_id} not found",
        )
    return MessageResponse(
        message=f"Successfully deleted snapshot {snapshot_id}",
        details={"snapshot_id": snapshot_id},
    )


# ============================================
# CHANGE DETECTION ENDPOINTS (SET OPERATIONS!)
# ============================================


@router.post(
    "/detect",
    response_model=ChangeDetectionResponse,
    status_code=status.HTTP_201_CREATED,
)
def detect_changes(
    request: ChangeDetectionRequest,
    db: Session = Depends(get_db),
):
    """
    Detect changes between two user snapshots using SET operations.

    **SET OPERATIONS USED:**
    - **NEW USERS**: snapshot_2 - snapshot_1 (DIFFERENCE - users who joined)
    - **CHURNED USERS**: snapshot_1 - snapshot_2 (DIFFERENCE - users who left)
    - **RETAINED USERS**: snapshot_1 & snapshot_2 (INTERSECTION - users who stayed)

    **METRICS CALCULATED:**
    - **Growth Rate**: (new - churned) / snapshot_1 total × 100
    - **Churn Rate**: churned / snapshot_1 total × 100
    - **Retention Rate**: retained / snapshot_1 total × 100

    This is the core change detection using set operations!
    """
    try:
        result = ChangeDetectionService.detect_changes(db, request)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to detect changes: {str(e)}",
        )


@router.get("/detect", response_model=List[ChangeDetectionResponse])
def get_all_results(db: Session = Depends(get_db)):
    """
    Get all change detection results.

    Returns results sorted by creation date (most recent first).
    """
    results = ChangeDetectionService.get_all_results(db)
    return results


@router.get("/detect/{result_id}", response_model=ChangeDetectionResponse)
def get_result(
    result_id: int,
    db: Session = Depends(get_db),
):
    """
    Get a specific change detection result by ID.
    """
    result = ChangeDetectionService.get_result_by_id(db, result_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Change detection result with id {result_id} not found",
        )
    return result


@router.delete("/detect/{result_id}", response_model=MessageResponse)
def delete_result(
    result_id: int,
    db: Session = Depends(get_db),
):
    """
    Delete a change detection result by ID.
    """
    deleted = ChangeDetectionService.delete_result(db, result_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Change detection result with id {result_id} not found",
        )
    return MessageResponse(
        message=f"Successfully deleted change detection result {result_id}",
        details={"result_id": result_id},
    )
