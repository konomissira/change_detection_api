# Change Detection API

A production-ready FastAPI service for detecting changes between user snapshots using **SET operations** to identify new users, churned users, and retained users. Built as **Project 4 of 4** in a data structures portfolio series.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![Tests](https://img.shields.io/badge/Tests-18%20Passed-success)

---

## 📋 Table of Contents

-   [Overview](#overview)
-   [Features](#features)
-   [Tech Stack](#tech-stack)
-   [Installation](#installation)
-   [Usage](#usage)
-   [API Endpoints](#api-endpoints)
-   [SET Operations Explained](#set-operations-explained)
-   [Testing](#testing)
-   [Project Structure](#project-structure)
-   [Real-World Use Cases](#real-world-use-cases)
-   [Contributing](#contributing)
-   [License](#license)

---

## 🎯 Overview

This API demonstrates efficient change detection techniques for comparing user snapshots over time (daily, weekly, monthly) using **set intersection and difference operations**.

**Real-World Scenario:**

-   Yesterday: 10,000 active users
-   Today: 10,250 active users
-   **Who's new? Who churned? Who stayed?**

This API answers those questions **instantly** using SET operations!

---

## ✨ Features

### Core Functionality

-   **Create User Snapshots** - Store user IDs at different points in time
-   **Detect Changes** - Compare snapshots to find new, churned, and retained users
-   **Calculate Metrics** - Growth rate, churn rate, and retention rate
-   **Track Historical Data** - Store and query past comparisons

### Technical Features

-   **Fast SET Operations** - O(n) time complexity for change detection
-   **RESTful API** - Clean, documented endpoints with Swagger UI
-   **Docker Containerized** - Easy deployment and consistent environment
-   **Comprehensive Tests** - 18 pytest tests with 100% coverage
-   **Well Documented** - Complete API docs and usage examples
-   **Modern Python** - Type hints, async support, pyproject.toml

---

## Tech Stack

| Technology     | Version | Purpose          |
| -------------- | ------- | ---------------- |
| **Python**     | 3.11    | Core language    |
| **FastAPI**    | 0.104.1 | Web framework    |
| **PostgreSQL** | 15      | Database         |
| **SQLAlchemy** | 2.0.23  | ORM              |
| **Docker**     | Latest  | Containerization |
| **pytest**     | 7.4.3   | Testing          |
| **Pydantic**   | 2.5.0   | Data validation  |

---

## Installation

### Prerequisites

-   Docker & Docker Compose installed
-   Git

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/konomissira/change_detection_api.git
cd change_detection_api

# 2. Copy environment variables
cp .env.example .env

# 3. Build and start containers
docker compose up -d --build

# 4. Verify API is running
curl http://localhost:8000/health

# 5. Open Swagger UI
open http://localhost:8000/docs
```

**That's it!** The API is now running at `http://localhost:8000`

---

## 📖 Usage

### Option 1: Swagger UI (Interactive)

1. Open http://localhost:8000/docs
2. Use the interactive interface to:
    - Create snapshots
    - Detect changes
    - View results

### Option 2: Sample Data (Quick Demo)

```bash
# Load sample data automatically
docker compose exec api python data/seed_data.py
```

This creates:

-   13 user snapshots
-   9 change detection analyses
-   5 realistic scenarios (growth, spike, seasonal drop, etc.)

### Option 3: Manual Testing

See `data/README.md` for step-by-step manual testing guide.

---

## API Endpoints

### Health Check

```
GET  /              Health check
GET  /health        Detailed health status
```

### User Snapshots

```
POST   /api/v1/snapshots          Create a new snapshot
GET    /api/v1/snapshots          Get all snapshots
GET    /api/v1/snapshots/{id}     Get specific snapshot
DELETE /api/v1/snapshots/{id}     Delete snapshot
```

### Change Detection

```
POST   /api/v1/detect             Detect changes between snapshots
GET    /api/v1/detect             Get all detection results
GET    /api/v1/detect/{id}        Get specific result
DELETE /api/v1/detect/{id}        Delete result
```

### Example Request

**Create a snapshot:**

```bash
curl -X POST "http://localhost:8000/api/v1/snapshots" \
  -H "Content-Type: application/json" \
  -d '{
    "snapshot_date": "2024-11-01T00:00:00Z",
    "snapshot_name": "Monday Active Users",
    "user_ids": [101, 102, 103, 104, 105]
  }'
```

**Detect changes:**

```bash
curl -X POST "http://localhost:8000/api/v1/detect" \
  -H "Content-Type: application/json" \
  -d '{
    "comparison_name": "Monday vs Tuesday",
    "snapshot_1_id": 1,
    "snapshot_2_id": 2
  }'
```

---

## 🎓 SET Operations Explained

This project demonstrates three fundamental SET operations:

### 1. SET DIFFERENCE (A - B) → New Users

```python
snapshot_2_users - snapshot_1_users
# Users who joined between snapshots
```

**Example:**

-   Monday: `[101, 102, 103]`
-   Tuesday: `[102, 103, 104, 105]`
-   **New Users:** `[104, 105]` ← Tuesday - Monday

### 2. SET DIFFERENCE (B - A) → Churned Users

```python
snapshot_1_users - snapshot_2_users
# Users who left between snapshots
```

**Example:**

-   Monday: `[101, 102, 103]`
-   Tuesday: `[102, 103, 104, 105]`
-   **Churned Users:** `[101]` ← Monday - Tuesday

### 3. SET INTERSECTION (A ∩ B) → Retained Users

```python
snapshot_1_users & snapshot_2_users
# Users who stayed in both snapshots
```

**Example:**

-   Monday: `[101, 102, 103]`
-   Tuesday: `[102, 103, 104, 105]`
-   **Retained Users:** `[102, 103]` ← Monday ∩ Tuesday

### Calculated Metrics

```python
# Growth Rate: (new - churned) / original * 100
growth_rate = ((2 - 1) / 3) * 100 = 33.33%

# Churn Rate: churned / original * 100
churn_rate = (1 / 3) * 100 = 33.33%

# Retention Rate: retained / original * 100
retention_rate = (2 / 3) * 100 = 66.67%
```

---

## Testing

### Run All Tests

```bash
# Run tests
docker compose exec api pytest

# Run with verbose output
docker compose exec api pytest -v

# Run with coverage report
docker compose exec api pytest --cov=app --cov-report=term-missing
```

### Test Coverage

| Module           | Tests  | Coverage |
| ---------------- | ------ | -------- |
| Health endpoints | 2      | 100%     |
| Snapshot CRUD    | 8      | 100%     |
| Change Detection | 8      | 100%     |
| **Total**        | **18** | **100%** |

**Test Scenarios:**

-   Create, read, update, delete snapshots
-   Duplicate snapshot name rejection
-   Change detection with growth
-   Change detection with churn
-   Perfect retention (no changes)
-   Complete turnover (all new users)
-   Invalid snapshot IDs

---

## 📁 Project Structure

```
change-detection-api/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   └── endpoints.py          # API routes
│   ├── __init__.py
│   ├── database.py               # Database connection
│   ├── main.py                   # FastAPI app
│   ├── models.py                 # SQLAlchemy models
│   ├── schemas.py                # Pydantic schemas
│   └── services.py               # Business logic (SET operations)
├── data/
│   ├── README.md                 # Manual testing guide
│   ├── sample_snapshots.json     # Sample data
│   └── seed_data.py              # Automated seeding script
├── tests/
│   ├── conftest.py               # Test fixtures
│   ├── test_change_detection.py  # Change detection tests
│   ├── test_health.py            # Health check tests
│   └── test_snapshots.py         # Snapshot CRUD tests
├── .dockerignore
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── LICENSE
├── pyproject.toml                # Modern Python config
├── README.md
└── requirements.txt
```

---

## 🌍 Real-World Use Cases

1. **Daily Active Users (DAU)** - Track day-over-day user changes
2. **Weekly Active Users (WAU)** - Monitor weekly engagement trends
3. **Product Launch Impact** - Measure user spike after feature releases
4. **Seasonal Patterns** - Understand holiday/seasonal behavior
5. **Churn Analysis** - Identify at-risk periods and user segments
6. **A/B Test Results** - Compare user retention between variants
7. **SaaS Metrics** - Calculate MRR churn, user retention cohorts
8. **Marketing Campaign ROI** - Track user acquisition from campaigns

---

## 🎨 Sample Scenarios (Included)

The seed script creates these realistic scenarios:

| Scenario            | Description             | Key Insight                 |
| ------------------- | ----------------------- | --------------------------- |
| **Weekly Growth**   | 4 weeks of user data    | Steady 10-15% weekly growth |
| **Product Launch**  | Before/after launch     | 150% user spike             |
| **Holiday Season**  | Seasonal activity drop  | 40% churn during holidays   |
| **Feature Removal** | User response to change | 25% churn after removal     |
| **Stable Period**   | Consecutive days        | 100% retention              |

---

## 🔧 Configuration

### Environment Variables

Edit `.env` file:

```env
# Database
POSTGRES_USER=change_user
POSTGRES_PASSWORD=change_password
POSTGRES_DB=change_detection_db
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Application
APP_HOST=0.0.0.0
APP_PORT=8000
```

### Docker Compose Services

-   **postgres** - PostgreSQL database (port 5432)
-   **api** - FastAPI application (port 8000)

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/YourFeatureName`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/YourFeatureName`)
5. Open a Pull Request

---

## 📊 Performance

-   **Time Complexity:** O(n) for change detection (SET operations)
-   **Space Complexity:** O(n) for storing user IDs
-   **Database Queries:** Optimised with indexes on date and name fields
-   **Response Time:** < 100ms for typical comparisons

---

## 📚 Documentation

-   **API Docs (Swagger):** http://localhost:8000/docs
-   **ReDoc:** http://localhost:8000/redoc
-   **Manual Testing Guide:** `data/README.md`
-   **Sample Data:** `data/sample_snapshots.json`

---

## 🐛 Troubleshooting

### Container won't start

```bash
docker compose down
docker volume prune
docker compose up -d --build
```

### Database connection error

```bash
# Check .env file has correct values
cat .env

# Restart containers
docker compose restart
```

### Tests failing

```bash
# Rebuild containers
docker compose down
docker compose up -d --build

# Run tests again
docker compose exec api pytest -v
```

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Mahamadou**

-   GitHub: [@konomissira](https://github.com/konomissira)

---

## Acknowledgments

This is **Project 4 of 4** in a data structures and algorithms portfolio series:

1. **Customer Deduplication API** - SET operations for deduplication
2. **Missing Orders API** - SET operations for finding missing data
3. **Transaction Reconciliation API** - SET operations for data reconciliation
4. **Change Detection API** - SET operations for detecting changes between user snapshots

Each project demonstrates practical applications of data structures in real-world data engineering scenarios.

---

## Next Steps

After exploring this project, consider:

1. **Extend functionality** - Add more metrics (cohort analysis, LTV calculations)
2. **Add authentication** - Implement JWT tokens for API security
3. **Deploy to cloud** - AWS, GCP, or Azure deployment
4. **Add caching** - Redis for frequently accessed comparisons
5. **Create dashboard** - Build a frontend with React/Vue.js
6. **Scale up** - Handle millions of users with batch processing

---

**Built with ❤️ using Python, FastAPI, and SET operations**

**⭐ Star this repo if you found it helpful!**
