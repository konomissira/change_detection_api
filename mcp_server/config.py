from pathlib import Path

# -------------------------
# Tool execution limits
# -------------------------

MAX_USER_IDS = 50_000
MAX_SNAPSHOT_NAME_LENGTH = 255
MAX_COMPARISON_NAME_LENGTH = 255

# -------------------------
# Governance flags
# -------------------------

ALLOW_WRITE_TOOLS = True

# -------------------------
# Audit logging
# -------------------------

AUDIT_LOG_DIR = Path("logs")
AUDIT_LOG_FILE = AUDIT_LOG_DIR / "mcp_audit.log"