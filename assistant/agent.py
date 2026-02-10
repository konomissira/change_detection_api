import re
from typing import Any, Dict, Optional, Tuple

import httpx

from assistant.config import ASSISTANT_API_BASE_URL, ASSISTANT_HTTP_TIMEOUT


def _extract_ints(text: str) -> list[int]:
    return [int(x) for x in re.findall(r"\b\d+\b", text)]


def _infer_action(message: str) -> Tuple[str, Dict[str, Any]]:
    # Rule-based router (v1).
    msg = message.strip().lower()

    # Health
    if "health" in msg or "status" in msg:
        return "health", {}

    # List snapshots
    if "list snapshots" in msg or ("snapshots" in msg and ("list" in msg or "show" in msg)):
        return "list_snapshots", {}

    # List detections
    if "list detections" in msg or ("detections" in msg and ("list" in msg or "show" in msg)):
        return "list_detections", {}

    # Get detection by id
    if "get detection" in msg or "detection id" in msg:
        ints = _extract_ints(msg)
        if ints:
            return "get_detection", {"detection_id": ints[0]}
        return "help", {"reason": "missing_detection_id"}

    # Detect changes between two snapshots
    if "detect" in msg or "compare" in msg or "churn" in msg or "retention" in msg:
        ints = _extract_ints(msg)
        if len(ints) >= 2:
            # Use first two ints as snapshot ids (simple v1)
            return "detect_changes", {"snapshot_1_id": ints[0], "snapshot_2_id": ints[1]}
        return "help", {"reason": "missing_snapshot_ids"}

    return "help", {"reason": "unknown_intent"}


async def _request(method: str, path: str, json: Optional[Dict[str, Any]] = None) -> Any:
    url = f"{ASSISTANT_API_BASE_URL}{path}"
    timeout = ASSISTANT_HTTP_TIMEOUT

    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.request(method, url, json=json)
        resp.raise_for_status()
        if resp.headers.get("content-type", "").startswith("application/json"):
            return resp.json()
        return {"raw": resp.text}


async def run_assistant(message: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Returns dict with:
      - action
      - result
      - explanation
    """
    action, params = _infer_action(message)

    # Allow deterministic overrides via metadata (optional)
    if metadata and isinstance(metadata, dict) and "action" in metadata:
        action = str(metadata["action"])
        params = dict(metadata.get("params", {}))

    if action == "health":
        data = await _request("GET", "/health")
        return {
            "action": "health",
            "result": data if isinstance(data, dict) else {"data": data},
            "explanation": "Health check completed successfully.",
        }

    if action == "list_snapshots":
        data = await _request("GET", "/api/v1/snapshots")
        count = len(data) if isinstance(data, list) else None
        return {
            "action": "list_snapshots",
            "result": {"count": count, "snapshots": data},
            "explanation": "Here are the available snapshots.",
        }

    if action == "list_detections":
        data = await _request("GET", "/api/v1/detect")
        count = len(data) if isinstance(data, list) else None
        return {
            "action": "list_detections",
            "result": {"count": count, "detections": data},
            "explanation": "Here are the stored change-detection results.",
        }

    if action == "get_detection":
        detection_id = int(params["detection_id"])
        data = await _request("GET", f"/api/v1/detect/{detection_id}")
        return {
            "action": "get_detection",
            "result": {"detection": data},
            "explanation": f"Fetched detection result #{detection_id}.",
        }

    if action == "detect_changes":
        s1 = int(params["snapshot_1_id"])
        s2 = int(params["snapshot_2_id"])

        # Derive a reasonable comparison name if user didn’t provide one
        comparison_name = params.get("comparison_name") or f"Snapshot {s1} vs {s2}"

        payload = {
            "comparison_name": comparison_name,
            "snapshot_1_id": s1,
            "snapshot_2_id": s2,
        }
        data = await _request("POST", "/api/v1/detect", json=payload)

        # Provide a more human-friendly explanation using returned metrics
        explanation = "Computed changes between the two snapshots."
        if isinstance(data, dict):
            metrics = data.get("metrics")
            if isinstance(metrics, dict):
                explanation = (
                    f"Between snapshot {s1} and {s2}, "
                    f"{metrics.get('new_users_count')} users joined, "
                    f"{metrics.get('churned_users_count')} users churned, "
                    f"and {metrics.get('retained_users_count')} users were retained. "
                    f"This represents a growth rate of {metrics.get('growth_rate')}% "
                    f"and a retention rate of {metrics.get('retention_rate')}%."
                )

        return {
            "action": "detect_changes",
            "result": {"analysis": data},
            "explanation": explanation,
        }

    # Help / fallback
    return {
        "action": "help",
        "result": {
            "examples": [
                "health",
                "list snapshots",
                "list detections",
                "get detection 1",
                "detect changes between snapshots 1 and 2",
            ],
            "hint": "Try including snapshot IDs for comparisons, e.g. 'compare 1 2'.",
            "reason": params.get("reason"),
        },
        "explanation": "I couldn’t confidently infer the action from your message. Try one of the examples.",
    }
