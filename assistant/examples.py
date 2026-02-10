from fastapi import APIRouter

router = APIRouter()


@router.get("/examples")
def examples():
    return {
        "examples": [
            {"prompt": "health", "description": "Check if the API is running"},
            {"prompt": "list snapshots", "description": "List all available user snapshots"},
            {"prompt": "list detections", "description": "List all stored change-detection results"},
            {"prompt": "get detection 1", "description": "Fetch a previous detection result by ID"},
            {"prompt": "compare snapshots 1 and 2", "description": "Detect new/churned/retained users and metrics"},
        ]
    }
