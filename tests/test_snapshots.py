from fastapi.testclient import TestClient
from datetime import datetime


def test_create_snapshot(client: TestClient):
    """Test creating a new user snapshot"""
    snapshot_data = {
        "snapshot_date": "2024-01-15T00:00:00Z",
        "snapshot_name": "Test Snapshot Monday",
        "user_ids": [101, 102, 103, 104, 105],
    }
    response = client.post("/api/v1/snapshots", json=snapshot_data)
    assert response.status_code == 201
    data = response.json()
    assert data["snapshot_name"] == "Test Snapshot Monday"
    assert data["total_users"] == 5
    assert len(data["user_ids"]) == 5
    assert "id" in data
    assert "created_at" in data


def test_create_duplicate_snapshot_name(client: TestClient):
    """Test that duplicate snapshot names are rejected"""
    snapshot_data = {
        "snapshot_date": "2024-01-15T00:00:00Z",
        "snapshot_name": "Duplicate Test",
        "user_ids": [101, 102, 103],
    }
    # Create first snapshot
    response1 = client.post("/api/v1/snapshots", json=snapshot_data)
    assert response1.status_code == 201

    # Try to create duplicate
    response2 = client.post("/api/v1/snapshots", json=snapshot_data)
    assert response2.status_code == 400
    assert "already exists" in response2.json()["detail"]


def test_get_all_snapshots_empty(client: TestClient):
    """Test getting all snapshots when none exist"""
    response = client.get("/api/v1/snapshots")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_get_all_snapshots(client: TestClient):
    """Test getting all snapshots"""
    # Create two snapshots
    snapshot1 = {
        "snapshot_date": "2024-01-15T00:00:00Z",
        "snapshot_name": "Snapshot 1",
        "user_ids": [101, 102, 103],
    }
    snapshot2 = {
        "snapshot_date": "2024-01-16T00:00:00Z",
        "snapshot_name": "Snapshot 2",
        "user_ids": [104, 105, 106],
    }
    client.post("/api/v1/snapshots", json=snapshot1)
    client.post("/api/v1/snapshots", json=snapshot2)

    # Get all snapshots
    response = client.get("/api/v1/snapshots")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_snapshot_by_id(client: TestClient):
    """Test getting a specific snapshot by ID"""
    # Create a snapshot
    snapshot_data = {
        "snapshot_date": "2024-01-15T00:00:00Z",
        "snapshot_name": "Test Snapshot",
        "user_ids": [101, 102, 103],
    }
    create_response = client.post("/api/v1/snapshots", json=snapshot_data)
    snapshot_id = create_response.json()["id"]

    # Get the snapshot
    response = client.get(f"/api/v1/snapshots/{snapshot_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == snapshot_id
    assert data["snapshot_name"] == "Test Snapshot"


def test_get_snapshot_not_found(client: TestClient):
    """Test getting a non-existent snapshot"""
    response = client.get("/api/v1/snapshots/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_delete_snapshot(client: TestClient):
    """Test deleting a snapshot"""
    # Create a snapshot
    snapshot_data = {
        "snapshot_date": "2024-01-15T00:00:00Z",
        "snapshot_name": "Test Snapshot",
        "user_ids": [101, 102, 103],
    }
    create_response = client.post("/api/v1/snapshots", json=snapshot_data)
    snapshot_id = create_response.json()["id"]

    # Delete the snapshot
    delete_response = client.delete(f"/api/v1/snapshots/{snapshot_id}")
    assert delete_response.status_code == 200
    assert "Successfully deleted" in delete_response.json()["message"]

    # Verify it's deleted
    get_response = client.get(f"/api/v1/snapshots/{snapshot_id}")
    assert get_response.status_code == 404


def test_delete_snapshot_not_found(client: TestClient):
    """Test deleting a non-existent snapshot"""
    response = client.delete("/api/v1/snapshots/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]