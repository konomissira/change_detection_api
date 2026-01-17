# MCP Server (Change Detection Tools)

This folder exposes the **Change Detection API** as **MCP tools** using the
**MCP Python SDK (FastMCP)**.

It allows AI assistants (e.g. Claude Desktop, Cursor, custom agents) to
interact with the API via structured tool calls instead of raw HTTP requests.

---

## 🚀 Run Locally (Recommended)

### 1 Start the Change Detection API

Make sure the FastAPI service is running (Docker or local):

-   API must be reachable at:
    ```
    http://localhost:8000
    ```

You can verify with:

```bash
curl http://localhost:8000/health
```

---

### 2 Install MCP dependencies

From your virtual environment:

```bash
pip install mcp httpx
```

---

### 3 Run the MCP Server

From the project root:

```bash
export CHANGE_API_BASE_URL="http://localhost:8000"
python -m mcp_server.server
```

By default, the MCP server runs over **stdio**, which is ideal for local
AI clients like Claude Desktop.

---

## 🤖 Claude Desktop Configuration Example

Add the following entry to your Claude Desktop configuration file:

```json
{
    "mcpServers": {
        "change_detection": {
            "command": "python",
            "args": ["-m", "mcp_server.server"],
            "env": {
                "CHANGE_API_BASE_URL": "http://localhost:8000"
            }
        }
    }
}
```

Restart Claude Desktop after saving the config.

---

## 🧰 Available MCP Tools

Once connected, the assistant can call the following tools:

-   `health()`  
    Check API health status

-   `list_snapshots()`  
    Retrieve all stored user snapshots

-   `create_snapshot(snapshot_date, snapshot_name, user_ids)`  
    Create a new user snapshot

-   `detect_changes(comparison_name, snapshot_1_id, snapshot_2_id)`  
    Compare two snapshots and compute growth, churn, and retention

-   `list_detections()`  
    List all historical change detection results

-   `get_detection(detection_id)`  
    Fetch a specific detection result

Each tool is strongly typed and validated before execution.

---

## 🧠 Design Notes

-   The MCP server **does not access the database directly**
-   It communicates with the API **via HTTP**
-   This keeps:
    -   clear separation of concerns
    -   easier security and governance
    -   safer AI tool execution

---

## 🔐 Governance (Coming Next)

Future iterations will add:

-   Tool allowlists and policies
-   Input size limits
-   Audit logging of tool calls
-   Authentication / authorisation hooks

---

## 📦 Package Marker

This folder is a Python package.

See:

```
mcp_server/__init__.py
```
