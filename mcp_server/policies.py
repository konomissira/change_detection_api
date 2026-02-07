from typing import Any, Dict

from mcp_server.config import (
    ALLOW_WRITE_TOOLS,
    MAX_COMPARISON_NAME_LENGTH,
    MAX_SNAPSHOT_NAME_LENGTH,
    MAX_USER_IDS,
)

# -------------------------
# Tool classification
# -------------------------

READ_TOOLS = {
    "health",
    "list_snapshots",
    "list_detections",
    "get_detection",
}

WRITE_TOOLS = {
    "create_snapshot",
    "detect_changes",
}


def validate_tool_allowed(tool_name: str) -> None:
    if tool_name in WRITE_TOOLS and not ALLOW_WRITE_TOOLS:
        raise PermissionError(f"Write tool '{tool_name}' is disabled")


def validate_tool_inputs(tool_name: str, args: Dict[str, Any]) -> None:
    """
    Enforce per-tool input constraints.
    """
    if tool_name == "create_snapshot":
        user_ids = args.get("user_ids", [])
        name = args.get("snapshot_name", "")

        if len(user_ids) > MAX_USER_IDS:
            raise ValueError(f"user_ids exceeds limit ({MAX_USER_IDS})")

        if len(name) > MAX_SNAPSHOT_NAME_LENGTH:
            raise ValueError("snapshot_name too long")

    if tool_name == "detect_changes":
        name = args.get("comparison_name", "")

        if len(name) > MAX_COMPARISON_NAME_LENGTH:
            raise ValueError("comparison_name too long")
