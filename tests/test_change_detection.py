from fastapi.testclient import TestClient


def test_detect_changes_success(client: TestClient):
    """
    Test change detection between two snapshots using SET operations.
    
    Scenario:
    - Snapshot 1 (Yesterday): [101, 102, 103, 104, 105]
    - Snapshot 2 (Today): [103, 104, 105, 106, 107]
    
    Expected Results (SET operations):
    - NEW USERS (snapshot_2 - snapshot_1): [106, 107]
    - CHURNED USERS (snapshot_1 - snapshot_2): [101, 102]
    - RETAINED USERS (snapshot_1 & snapshot_2): [103, 104, 105]
    """
    # Create snapshot 1 (yesterday)
    snapshot1_data = {
        "snapshot_date": "2024-01-15T00:00:00Z",
        "snapshot_name": "Yesterday Users",
        "user_ids": [101, 102, 103, 104, 105],
    }
    response1 = client.post("/api/v1/snapshots", json=snapshot1_data)
    snapshot1_id = response1.json()["id"]

    # Create snapshot 2 (today)
    snapshot2_data = {
        "snapshot_date": "2024-01-16T00:00:00Z",
        "snapshot_name": "Today Users",
        "user_ids": [103, 104, 105, 106, 107],
    }
    response2 = client.post("/api/v1/snapshots", json=snapshot2_data)
    snapshot2_id = response2.json()["id"]

    # Detect changes
    detection_request = {
        "comparison_name": "Yesterday vs Today",
        "snapshot_1_id": snapshot1_id,
        "snapshot_2_id": snapshot2_id,
    }
    response = client.post("/api/v1/detect", json=detection_request)
    assert response.status_code == 201
    data = response.json()

    # Verify SET operations results
    assert set(data["new_users"]) == {106, 107}  # New users
    assert set(data["churned_users"]) == {101, 102}  # Churned users
    assert set(data["retained_users"]) == {103, 104, 105}  # Retained users

    # Verify metrics
    metrics = data["metrics"]
    assert metrics["new_users_count"] == 2
    assert metrics["churned_users_count"] == 2
    assert metrics["retained_users_count"] == 3

    # Growth rate: (2 new - 2 churned) / 5 original * 100 = 0%
    assert metrics["growth_rate"] == 0.0

    # Churn rate: 2 churned / 5 original * 100 = 40%
    assert metrics["churn_rate"] == 40.0

    # Retention rate: 3 retained / 5 original * 100 = 60%
    assert metrics["retention_rate"] == 60.0


def test_detect_changes_all_new_users(client: TestClient):
    """
    Test when all users in snapshot 2 are new.
    
    Scenario:
    - Snapshot 1: [101, 102, 103]
    - Snapshot 2: [201, 202, 203]
    
    Expected:
    - NEW: [201, 202, 203]
    - CHURNED: [101, 102, 103]
    - RETAINED: []
    """
    # Create snapshots
    snapshot1 = {
        "snapshot_date": "2024-01-15T00:00:00Z",
        "snapshot_name": "Old Users",
        "user_ids": [101, 102, 103],
    }
    snapshot2 = {
        "snapshot_date": "2024-01-16T00:00:00Z",
        "snapshot_name": "All New Users",
        "user_ids": [201, 202, 203],
    }
    s1_id = client.post("/api/v1/snapshots", json=snapshot1).json()["id"]
    s2_id = client.post("/api/v1/snapshots", json=snapshot2).json()["id"]

    # Detect changes
    request = {
        "comparison_name": "Complete Turnover",
        "snapshot_1_id": s1_id,
        "snapshot_2_id": s2_id,
    }
    response = client.post("/api/v1/detect", json=request)
    data = response.json()

    assert set(data["new_users"]) == {201, 202, 203}
    assert set(data["churned_users"]) == {101, 102, 103}
    assert len(data["retained_users"]) == 0
    assert data["metrics"]["retention_rate"] == 0.0
    assert data["metrics"]["churn_rate"] == 100.0


def test_detect_changes_no_changes(client: TestClient):
    """
    Test when both snapshots have identical users.
    
    Scenario:
    - Snapshot 1: [101, 102, 103]
    - Snapshot 2: [101, 102, 103]
    
    Expected:
    - NEW: []
    - CHURNED: []
    - RETAINED: [101, 102, 103]
    """
    user_ids = [101, 102, 103]
    snapshot1 = {
        "snapshot_date": "2024-01-15T00:00:00Z",
        "snapshot_name": "Stable Users 1",
        "user_ids": user_ids,
    }
    snapshot2 = {
        "snapshot_date": "2024-01-16T00:00:00Z",
        "snapshot_name": "Stable Users 2",
        "user_ids": user_ids,
    }
    s1_id = client.post("/api/v1/snapshots", json=snapshot1).json()["id"]
    s2_id = client.post("/api/v1/snapshots", json=snapshot2).json()["id"]

    # Detect changes
    request = {
        "comparison_name": "No Changes",
        "snapshot_1_id": s1_id,
        "snapshot_2_id": s2_id,
    }
    response = client.post("/api/v1/detect", json=request)
    data = response.json()

    assert len(data["new_users"]) == 0
    assert len(data["churned_users"]) == 0
    assert set(data["retained_users"]) == {101, 102, 103}
    assert data["metrics"]["retention_rate"] == 100.0
    assert data["metrics"]["churn_rate"] == 0.0
    assert data["metrics"]["growth_rate"] == 0.0


def test_detect_changes_growth(client: TestClient):
    """
    Test user growth scenario.
    
    Scenario:
    - Snapshot 1: [101, 102, 103, 104, 105] (5 users)
    - Snapshot 2: [101, 102, 103, 104, 105, 106, 107, 108] (8 users)
    
    Expected:
    - NEW: [106, 107, 108]
    - CHURNED: []
    - RETAINED: [101, 102, 103, 104, 105]
    - Growth: +60%
    """
    snapshot1 = {
        "snapshot_date": "2024-01-15T00:00:00Z",
        "snapshot_name": "Before Growth",
        "user_ids": [101, 102, 103, 104, 105],
    }
    snapshot2 = {
        "snapshot_date": "2024-01-16T00:00:00Z",
        "snapshot_name": "After Growth",
        "user_ids": [101, 102, 103, 104, 105, 106, 107, 108],
    }
    s1_id = client.post("/api/v1/snapshots", json=snapshot1).json()["id"]
    s2_id = client.post("/api/v1/snapshots", json=snapshot2).json()["id"]

    request = {
        "comparison_name": "Growth Period",
        "snapshot_1_id": s1_id,
        "snapshot_2_id": s2_id,
    }
    response = client.post("/api/v1/detect", json=request)
    data = response.json()

    assert set(data["new_users"]) == {106, 107, 108}
    assert len(data["churned_users"]) == 0
    assert data["metrics"]["new_users_count"] == 3
    assert data["metrics"]["growth_rate"] == 60.0  # 3 / 5 * 100


def test_detect_changes_snapshot_not_found(client: TestClient):
    """Test change detection with non-existent snapshot IDs"""
    request = {
        "comparison_name": "Invalid Test",
        "snapshot_1_id": 999,
        "snapshot_2_id": 998,
    }
    response = client.post("/api/v1/detect", json=request)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_get_all_detection_results(client: TestClient):
    """Test getting all change detection results"""
    # Create snapshots and detect changes
    snapshot1 = {
        "snapshot_date": "2024-01-15T00:00:00Z",
        "snapshot_name": "Test 1",
        "user_ids": [101, 102],
    }
    snapshot2 = {
        "snapshot_date": "2024-01-16T00:00:00Z",
        "snapshot_name": "Test 2",
        "user_ids": [102, 103],
    }
    s1_id = client.post("/api/v1/snapshots", json=snapshot1).json()["id"]
    s2_id = client.post("/api/v1/snapshots", json=snapshot2).json()["id"]

    request = {
        "comparison_name": "Test Comparison",
        "snapshot_1_id": s1_id,
        "snapshot_2_id": s2_id,
    }
    client.post("/api/v1/detect", json=request)

    # Get all results
    response = client.get("/api/v1/detect")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["comparison_name"] == "Test Comparison"


def test_get_detection_result_by_id(client: TestClient):
    """Test getting a specific detection result by ID"""
    # Create and detect
    snapshot1 = {
        "snapshot_date": "2024-01-15T00:00:00Z",
        "snapshot_name": "S1",
        "user_ids": [101],
    }
    snapshot2 = {
        "snapshot_date": "2024-01-16T00:00:00Z",
        "snapshot_name": "S2",
        "user_ids": [102],
    }
    s1_id = client.post("/api/v1/snapshots", json=snapshot1).json()["id"]
    s2_id = client.post("/api/v1/snapshots", json=snapshot2).json()["id"]

    request = {"comparison_name": "Test", "snapshot_1_id": s1_id, "snapshot_2_id": s2_id}
    create_response = client.post("/api/v1/detect", json=request)
    result_id = create_response.json()["id"]

    # Get by ID
    response = client.get(f"/api/v1/detect/{result_id}")
    assert response.status_code == 200
    assert response.json()["id"] == result_id


def test_delete_detection_result(client: TestClient):
    """Test deleting a detection result"""
    # Create and detect
    snapshot1 = {
        "snapshot_date": "2024-01-15T00:00:00Z",
        "snapshot_name": "S1",
        "user_ids": [101],
    }
    snapshot2 = {
        "snapshot_date": "2024-01-16T00:00:00Z",
        "snapshot_name": "S2",
        "user_ids": [102],
    }
    s1_id = client.post("/api/v1/snapshots", json=snapshot1).json()["id"]
    s2_id = client.post("/api/v1/snapshots", json=snapshot2).json()["id"]

    request = {"comparison_name": "Test", "snapshot_1_id": s1_id, "snapshot_2_id": s2_id}
    create_response = client.post("/api/v1/detect", json=request)
    result_id = create_response.json()["id"]

    # Delete
    delete_response = client.delete(f"/api/v1/detect/{result_id}")
    assert delete_response.status_code == 200

    # Verify deleted
    get_response = client.get(f"/api/v1/detect/{result_id}")
    assert get_response.status_code == 404