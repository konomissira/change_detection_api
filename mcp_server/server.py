import os
import httpx
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from mcp_server.audit import log_tool_call
from mcp_server.policies import validate_tool_allowed, validate_tool_inputs


mcp = FastMCP("Change Detection API - MCP Tools")

BASE_URL = os.getenv("CHANGE_API_BASE_URL", "http://localhost:8000").rstrip("/")
DEFAULT_TIMEOUT = float(os.getenv("MCP_HTTP_TIMEOUT", "15"))


async def _request(method: str, path: str, json: Optional[Dict[str, Any]] = None) -> Any:
    url = f"{BASE_URL}{path}"

    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        resp = await client.request(method, url, json=json)
        resp.raise_for_status()
        if resp.headers.get("content-type", "").startswith("application/json"):
            return resp.json()
        return resp.text


# -------------------------
# READ tools
# -------------------------

@mcp.tool()
async def health() -> Dict[str, Any]:
    """Check the API health (calls GET /health)."""
    tool_name = "health"
    audit_args: Dict[str, Any] = {}

    try:
        validate_tool_allowed(tool_name)
        validate_tool_inputs(tool_name, {})

        result = await _request("GET", "/health")

        log_tool_call(tool_name=tool_name, arguments=audit_args, success=True)
        return result

    except Exception as exc:
        log_tool_call(tool_name=tool_name, arguments=audit_args, success=False, error=str(exc))
        raise


@mcp.tool()
async def list_snapshots() -> List[Dict[str, Any]]:
    """List all snapshots (calls GET /api/v1/snapshots)."""
    tool_name = "list_snapshots"
    audit_args: Dict[str, Any] = {}

    try:
        validate_tool_allowed(tool_name)
        validate_tool_inputs(tool_name, {})

        result = await _request("GET", "/api/v1/snapshots")

        log_tool_call(tool_name=tool_name, arguments=audit_args, success=True)
        return result

    except Exception as exc:
        log_tool_call(tool_name=tool_name, arguments=audit_args, success=False, error=str(exc))
        raise


@mcp.tool()
async def list_detections() -> List[Dict[str, Any]]:
    """List all detection runs (calls GET /api/v1/detect)."""
    tool_name = "list_detections"
    audit_args: Dict[str, Any] = {}

    try:
        validate_tool_allowed(tool_name)
        validate_tool_inputs(tool_name, {})

        result = await _request("GET", "/api/v1/detect")

        log_tool_call(tool_name=tool_name, arguments=audit_args, success=True)
        return result

    except Exception as exc:
        log_tool_call(tool_name=tool_name, arguments=audit_args, success=False, error=str(exc))
        raise


@mcp.tool()
async def get_detection(detection_id: int) -> Dict[str, Any]:
    """Get a specific detection result (calls GET /api/v1/detect/{id})."""
    tool_name = "get_detection"
    audit_args = {"detection_id": detection_id}

    try:
        validate_tool_allowed(tool_name)
        validate_tool_inputs(tool_name, audit_args)

        result = await _request("GET", f"/api/v1/detect/{detection_id}")

        log_tool_call(tool_name=tool_name, arguments=audit_args, success=True)
        return result

    except Exception as exc:
        log_tool_call(tool_name=tool_name, arguments=audit_args, success=False, error=str(exc))
        raise


# -------------------------
# WRITE tools
# -------------------------

@mcp.tool()
async def create_snapshot(
    snapshot_date: str,
    snapshot_name: str,
    user_ids: List[int],
) -> Dict[str, Any]:
    """
    Create a snapshot (calls POST /api/v1/snapshots).
    """
    tool_name = "create_snapshot"

    payload = {
        "snapshot_date": snapshot_date,
        "snapshot_name": snapshot_name,
        "user_ids": user_ids,
    }

    # Safer audit payload (no raw IDs)
    audit_args = {
        "snapshot_name": snapshot_name,
        "user_count": len(user_ids),
    }

    try:
        validate_tool_allowed(tool_name)
        validate_tool_inputs(tool_name, payload)

        result = await _request("POST", "/api/v1/snapshots", json=payload)

        log_tool_call(tool_name=tool_name, arguments=audit_args, success=True)
        return result

    except Exception as exc:
        log_tool_call(tool_name=tool_name, arguments=audit_args, success=False, error=str(exc))
        raise


@mcp.tool()
async def detect_changes(
    comparison_name: str,
    snapshot_1_id: int,
    snapshot_2_id: int,
) -> Dict[str, Any]:
    """Detect changes (calls POST /api/v1/detect)."""
    tool_name = "detect_changes"

    payload = {
        "comparison_name": comparison_name,
        "snapshot_1_id": snapshot_1_id,
        "snapshot_2_id": snapshot_2_id,
    }

    audit_args = {
        "comparison_name": comparison_name,
        "snapshot_1_id": snapshot_1_id,
        "snapshot_2_id": snapshot_2_id,
    }

    try:
        validate_tool_allowed(tool_name)
        validate_tool_inputs(tool_name, payload)

        result = await _request("POST", "/api/v1/detect", json=payload)

        log_tool_call(tool_name=tool_name, arguments=audit_args, success=True)
        return result

    except Exception as exc:
        log_tool_call(tool_name=tool_name, arguments=audit_args, success=False, error=str(exc))
        raise


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
