# Sample Data & Manual Testing Guide

This directory contains sample data for testing the Change Detection API.

## Files

-   **`sample_snapshots.json`** - Pre-configured user snapshots and comparison scenarios
-   **`seed_data.py`** - Automated script to populate the database

## Manual Testing via Swagger UI

### Prerequisites

1. Start the API:

```bash
docker compose up -d --build
```

2. Open Swagger UI:

```
http://localhost:8000/docs
```

---

## Step-by-Step Testing Guide

### Step 1: Create User Snapshots

Use the sample data from `sample_snapshots.json` to create snapshots.

#### Example 1: Create Monday Snapshot

1. Go to **POST /api/v1/snapshots**
2. Click "Try it out"
3. Paste this JSON:

```json
{
    "snapshot_date": "2024-11-01T00:00:00Z",
    "snapshot_name": "Monday Active Users",
    "user_ids": [101, 102, 103, 104, 105, 106, 107, 108, 109, 110]
}
```

4. Click "Execute"
5. **Note the `id` from the response** (e.g., `id: 1`)

#### Example 2: Create Tuesday Snapshot

Repeat with Tuesday data:

```json
{
    "snapshot_date": "2024-11-02T00:00:00Z",
    "snapshot_name": "Tuesday Active Users",
    "user_ids": [102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112]
}
```

**Note the `id`** (e.g., `id: 2`)

---

### Step 2: View All Snapshots

1. Go to **GET /api/v1/snapshots**
2. Click "Try it out"
3. Click "Execute"
4. You should see both snapshots listed

---

### Step 3: Detect Changes Between Snapshots

Now let's compare Monday vs Tuesday using SET operations!

1. Go to **POST /api/v1/detect**
2. Click "Try it out"
3. Paste this JSON (use your actual snapshot IDs):

```json
{
    "comparison_name": "Monday vs Tuesday Growth",
    "snapshot_1_id": 1,
    "snapshot_2_id": 2
}
```

4. Click "Execute"

#### Expected Results:

```json
{
    "id": 1,
    "comparison_name": "Monday vs Tuesday Growth",
    "snapshot_1_id": 1,
    "snapshot_2_id": 2,
    "snapshot_1_date": "2024-11-01T00:00:00Z",
    "snapshot_2_date": "2024-11-02T00:00:00Z",
    "new_users": [111, 112], // SET DIFFERENCE (Tuesday - Monday)
    "churned_users": [101], // SET DIFFERENCE (Monday - Tuesday)
    "retained_users": [102, 103, 104, 105, 106, 107, 108, 109, 110], // SET INTERSECTION
    "metrics": {
        "new_users_count": 2,
        "churned_users_count": 1,
        "retained_users_count": 9,
        "growth_rate": 10.0, // (2 new - 1 churned) / 10 original * 100
        "churn_rate": 10.0, // 1 churned / 10 original * 100
        "retention_rate": 90.0 // 9 retained / 10 original * 100
    }
}
```

**🎉 SET Operations Explained:**

-   **NEW USERS** = Tuesday users - Monday users = `[111, 112]`
-   **CHURNED USERS** = Monday users - Tuesday users = `[101]`
-   **RETAINED USERS** = Monday users ∩ Tuesday users = `[102-110]`

---

### Step 4: View All Change Detection Results

1. Go to **GET /api/v1/detect**
2. Click "Try it out"
3. Click "Execute"
4. See all your change detection analyses

---

## Pre-Built Testing Scenarios

Use these scenarios from `sample_snapshots.json`:

### Scenario 1: Product Launch Impact 🚀

**Before Launch:**

```json
{
    "snapshot_date": "2024-10-01T00:00:00Z",
    "snapshot_name": "Before Product Launch",
    "user_ids": [301, 302, 303, 304, 305, 306, 307, 308, 309, 310]
}
```

**After Launch:**

```json
{
    "snapshot_date": "2024-10-02T00:00:00Z",
    "snapshot_name": "After Product Launch",
    "user_ids": [
        301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314,
        315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325
    ]
}
```

**Expected Results:**

-   ✅ 15 new users (150% growth!)
-   ✅ 0 churned users (perfect retention)
-   ✅ 10 retained users

---

### Scenario 2: Holiday Season Impact 🎄

**Before Holidays:**

```json
{
    "snapshot_date": "2024-12-15T00:00:00Z",
    "snapshot_name": "Before Holidays",
    "user_ids": [
        401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414,
        415, 416, 417, 418, 419, 420
    ]
}
```

**During Holidays:**

```json
{
    "snapshot_date": "2024-12-25T00:00:00Z",
    "snapshot_name": "During Holidays",
    "user_ids": [401, 403, 405, 407, 409, 411, 413, 415, 417, 419, 421, 422]
}
```

**Expected Results:**

-   ⚠️ 2 new users
-   ⚠️ 10 churned users (50% churn!)
-   ✅ 10 retained users

---

### Scenario 3: Weekly Growth 📈

**Week 1:**

```json
{
    "snapshot_date": "2024-11-08T00:00:00Z",
    "snapshot_name": "Week 1 - Active Users",
    "user_ids": [
        201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214,
        215
    ]
}
```

**Week 2:**

```json
{
    "snapshot_date": "2024-11-15T00:00:00Z",
    "snapshot_name": "Week 2 - Active Users",
    "user_ids": [
        202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215,
        216, 217, 218, 219, 220
    ]
}
```

**Expected Results:**

-   ✅ 5 new users
-   ⚠️ 1 churned user
-   ✅ 14 retained users
-   📊 Growth rate: ~27%

---

## Testing Individual Endpoints

### Get a Specific Snapshot

1. Go to **GET /api/v1/snapshots/{snapshot_id}**
2. Enter a snapshot ID (e.g., `1`)
3. Click "Execute"

### Delete a Snapshot

1. Go to **DELETE /api/v1/snapshots/{snapshot_id}**
2. Enter a snapshot ID
3. Click "Execute"

### Get a Specific Detection Result

1. Go to **GET /api/v1/detect/{result_id}**
2. Enter a result ID
3. Click "Execute"

### Delete a Detection Result

1. Go to **DELETE /api/v1/detect/{result_id}**
2. Enter a result ID
3. Click "Execute"

---

## Understanding the Metrics

### Growth Rate

```
(New Users - Churned Users) / Original Total * 100
```

-   Positive = Growth
-   Negative = Decline
-   Zero = Stable

### Churn Rate

```
Churned Users / Original Total * 100
```

-   Lower is better
-   Industry average: 5-7% monthly

### Retention Rate

```
Retained Users / Original Total * 100
```

-   Higher is better
-   Aim for 80%+ for healthy products

---

## Real-World Use Cases

1. **Daily Active Users (DAU)** - Track day-over-day changes
2. **Weekly Active Users (WAU)** - Monitor weekly trends
3. **Product Launch Impact** - Measure feature releases
4. **Seasonal Patterns** - Understand holiday/seasonal behavior
5. **Churn Analysis** - Identify at-risk periods
6. **A/B Test Results** - Compare user behavior between variants

---

## Tips for Testing

1. **Start Simple** - Begin with 2 snapshots, then expand
2. **Use Clear Names** - Descriptive snapshot names help tracking
3. **Track IDs** - Keep note of snapshot/result IDs for comparisons
4. **Check Metrics** - Verify calculations make sense
5. **Try Edge Cases** - Test with identical snapshots, empty sets, etc.

---

## Automated Testing Alternative

If you prefer automated seeding:

```bash
# Run inside Docker container (recommended)
docker compose exec api python data/seed_data.py

# Or run locally (requires: pip install requests)
python data/seed_data.py
```

This creates 13 snapshots and 9 comparisons automatically!

---

## Need Help?

-   Check the main README.md for project overview
-   View API documentation: http://localhost:8000/docs
-   Run tests: `docker compose exec api pytest -v`
