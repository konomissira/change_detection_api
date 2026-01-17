import os
import httpx
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

# MCP Server name (shows up in clients)
mcp = FastMCP("Change Detection API - MCP Tools")

BASE_URL = os.getenv("CHANGE_API_BASE_URL", "http://localhost:8000").rstrip("/")


async def _request(method: str, path: str, json: Optional[Dict[str, Any]] = None) -> Any:
    url = f"{BASE_URL}{path}"
    timeout = float(os.getenv("MCP_HTTP_TIMEOUT", "15"))

    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.request(method, url, json=json)
        resp.raise_for_status()
        if resp.headers.get("content-type", "").startswith("application/json"):
            return resp.json()
        return resp.text


@mcp.tool()
async def health() -> Dict[str, Any]:
    """Check the API health (calls GET /health)."""
    return await _request("GET", "/health")


@mcp.tool()
async def list_snapshots() -> List[Dict[str, Any]]:
    """List all snapshots (calls GET /api/v1/snapshots)."""
    return await _request("GET", "/api/v1/snapshots")


@mcp.tool()
async def create_snapshot(
    snapshot_date: str,
    snapshot_name: str,
    user_ids: List[int],
) -> Dict[str, Any]:
    """
    Create a snapshot (calls POST /api/v1/snapshots).

    snapshot_date: ISO8601 string, e.g. "2024-11-01T00:00:00Z"
    snapshot_name: friendly label
    user_ids: list of user IDs
    """
    payload = {
        "snapshot_date": snapshot_date,
        "snapshot_name": snapshot_name,
        "user_ids": user_ids,
    }
    return await _request("POST", "/api/v1/snapshots", json=payload)


@mcp.tool()
async def detect_changes(
    comparison_name: str,
    snapshot_1_id: int,
    snapshot_2_id: int,
) -> Dict[str, Any]:
    """Detect changes (calls POST /api/v1/detect)."""
    payload = {
        "comparison_name": comparison_name,
        "snapshot_1_id": snapshot_1_id,
        "snapshot_2_id": snapshot_2_id,
    }
    return await _request("POST", "/api/v1/detect", json=payload)


@mcp.tool()
async def list_detections() -> List[Dict[str, Any]]:
    """List all detection runs (calls GET /api/v1/detect)."""
    return await _request("GET", "/api/v1/detect")


@mcp.tool()
async def get_detection(detection_id: int) -> Dict[str, Any]:
    """Get a specific detection result (calls GET /api/v1/detect/{id})."""
    return await _request("GET", f"/api/v1/detect/{detection_id}")


def main() -> None:
    # Default transport is stdio (works well for Claude Desktop/Cursor-style clients)
    mcp.run()


if __name__ == "__main__":
    main()
