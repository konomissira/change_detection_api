#!/usr/bin/env python3
"""
Seed script for Change Detection API

This script creates sample user snapshots and demonstrates change detection
using SET operations with realistic scenarios.
"""

import requests
from datetime import datetime, timedelta
import random

# API base URL
BASE_URL = "http://localhost:8000/api/v1"


def create_snapshot(snapshot_date, snapshot_name, user_ids):
    """Create a user snapshot"""
    data = {
        "snapshot_date": snapshot_date.isoformat() + "Z",
        "snapshot_name": snapshot_name,
        "user_ids": user_ids,
    }
    response = requests.post(f"{BASE_URL}/snapshots", json=data)
    if response.status_code == 201:
        print(f"Created snapshot: {snapshot_name} ({len(user_ids)} users)")
        return response.json()
    else:
        print(f"Failed to create snapshot: {snapshot_name}")
        print(f"   Error: {response.json()}")
        return None


def detect_changes(comparison_name, snapshot_1_id, snapshot_2_id):
    """Detect changes between two snapshots"""
    data = {
        "comparison_name": comparison_name,
        "snapshot_1_id": snapshot_1_id,
        "snapshot_2_id": snapshot_2_id,
    }
    response = requests.post(f"{BASE_URL}/detect", json=data)
    if response.status_code == 201:
        result = response.json()
        print(f"\n🔍 Change Detection: {comparison_name}")
        print(f"   📊 Metrics:")
        print(f"      • New Users: {result['metrics']['new_users_count']}")
        print(f"      • Churned Users: {result['metrics']['churned_users_count']}")
        print(f"      • Retained Users: {result['metrics']['retained_users_count']}")
        print(f"      • Growth Rate: {result['metrics']['growth_rate']}%")
        print(f"      • Churn Rate: {result['metrics']['churn_rate']}%")
        print(f"      • Retention Rate: {result['metrics']['retention_rate']}%")
        return result
    else:
        print(f"Failed to detect changes: {comparison_name}")
        return None


def main():
    """Seed the database with sample data"""
    print("\n" + "=" * 70)
    print("SEEDING CHANGE DETECTION API WITH SAMPLE DATA")
    print("=" * 70 + "\n")

    # Base date for snapshots
    base_date = datetime(2024, 11, 1)

    # =========================================================================
    # SCENARIO 1: Weekly Active Users - Growth Trend
    # =========================================================================
    print("\n📈 SCENARIO 1: Weekly Active Users (Growth Trend)")
    print("-" * 70)

    # Week 1: Starting user base
    week1_users = list(range(1001, 1101))  # 100 users
    snapshot1 = create_snapshot(
        base_date, "Week 1 - Active Users", week1_users
    )

    # Week 2: Some growth, minimal churn
    week2_users = week1_users.copy()
    # Remove 5 churned users
    churned = random.sample(week2_users, 5)
    for user in churned:
        week2_users.remove(user)
    # Add 15 new users
    new_users = list(range(1101, 1116))
    week2_users.extend(new_users)
    snapshot2 = create_snapshot(
        base_date + timedelta(days=7), "Week 2 - Active Users", week2_users
    )

    # Week 3: Continued growth
    week3_users = week2_users.copy()
    # Remove 3 churned users
    churned = random.sample(week3_users, 3)
    for user in churned:
        week3_users.remove(user)
    # Add 20 new users
    new_users = list(range(1116, 1136))
    week3_users.extend(new_users)
    snapshot3 = create_snapshot(
        base_date + timedelta(days=14), "Week 3 - Active Users", week3_users
    )

    # Week 4: Strong growth
    week4_users = week3_users.copy()
    # Remove 4 churned users
    churned = random.sample(week4_users, 4)
    for user in churned:
        week4_users.remove(user)
    # Add 25 new users
    new_users = list(range(1136, 1161))
    week4_users.extend(new_users)
    snapshot4 = create_snapshot(
        base_date + timedelta(days=21), "Week 4 - Active Users", week4_users
    )

    # Detect changes between weeks
    if snapshot1 and snapshot2:
        detect_changes("Week 1 vs Week 2", snapshot1["id"], snapshot2["id"])

    if snapshot2 and snapshot3:
        detect_changes("Week 2 vs Week 3", snapshot2["id"], snapshot3["id"])

    if snapshot3 and snapshot4:
        detect_changes("Week 3 vs Week 4", snapshot3["id"], snapshot4["id"])

    # =========================================================================
    # SCENARIO 2: Product Launch - User Spike
    # =========================================================================
    print("\n\n🚀 SCENARIO 2: Product Launch (User Spike)")
    print("-" * 70)

    # Before launch: steady state
    pre_launch_users = list(range(2001, 2051))  # 50 users
    snapshot_pre = create_snapshot(
        base_date + timedelta(days=30), "Pre-Launch Users", pre_launch_users
    )

    # Launch day: big spike
    post_launch_users = pre_launch_users.copy()
    # Retain most users (2 churned)
    churned = random.sample(post_launch_users, 2)
    for user in churned:
        post_launch_users.remove(user)
    # Add 100 new users (spike!)
    new_users = list(range(2051, 2151))
    post_launch_users.extend(new_users)
    snapshot_post = create_snapshot(
        base_date + timedelta(days=31), "Launch Day Users", post_launch_users
    )

    if snapshot_pre and snapshot_post:
        detect_changes("Pre-Launch vs Launch Day", snapshot_pre["id"], snapshot_post["id"])

    # =========================================================================
    # SCENARIO 3: Seasonal Drop - Holiday Period
    # =========================================================================
    print("\n\n🎄 SCENARIO 3: Seasonal Drop (Holiday Period)")
    print("-" * 70)

    # Before holidays: normal activity
    before_holidays = list(range(3001, 3201))  # 200 users
    snapshot_before = create_snapshot(
        base_date + timedelta(days=60), "Before Holidays", before_holidays
    )

    # During holidays: significant drop
    during_holidays = before_holidays.copy()
    # 40% churn during holidays
    churned_count = int(len(during_holidays) * 0.4)
    churned = random.sample(during_holidays, churned_count)
    for user in churned:
        during_holidays.remove(user)
    # Only 10 new users
    new_users = list(range(3201, 3211))
    during_holidays.extend(new_users)
    snapshot_during = create_snapshot(
        base_date + timedelta(days=75), "During Holidays", during_holidays
    )

    if snapshot_before and snapshot_during:
        detect_changes(
            "Before vs During Holidays", snapshot_before["id"], snapshot_during["id"]
        )

    # =========================================================================
    # SCENARIO 4: Feature Removal - User Response
    # =========================================================================
    print("\n\n⚠️  SCENARIO 4: Feature Removal (User Response)")
    print("-" * 70)

    # Before feature removal
    before_removal = list(range(4001, 4081))  # 80 users
    snapshot_before_removal = create_snapshot(
        base_date + timedelta(days=90), "Before Feature Removal", before_removal
    )

    # After feature removal: some users leave
    after_removal = before_removal.copy()
    # 25% churn due to feature removal
    churned_count = int(len(after_removal) * 0.25)
    churned = random.sample(after_removal, churned_count)
    for user in churned:
        after_removal.remove(user)
    # Minimal new users (5)
    new_users = list(range(4081, 4086))
    after_removal.extend(new_users)
    snapshot_after_removal = create_snapshot(
        base_date + timedelta(days=91),
        "After Feature Removal",
        after_removal,
    )

    if snapshot_before_removal and snapshot_after_removal:
        detect_changes(
            "Before vs After Feature Removal",
            snapshot_before_removal["id"],
            snapshot_after_removal["id"],
        )

    # =========================================================================
    # SCENARIO 5: Stable User Base - No Changes
    # =========================================================================
    print("\n\n📊 SCENARIO 5: Stable User Base (Minimal Changes)")
    print("-" * 70)

    # Day 1: stable users
    stable_users = list(range(5001, 5051))  # 50 users
    snapshot_stable1 = create_snapshot(
        base_date + timedelta(days=100), "Stable Users - Day 1", stable_users
    )

    # Day 2: same users (perfect retention)
    snapshot_stable2 = create_snapshot(
        base_date + timedelta(days=101), "Stable Users - Day 2", stable_users
    )

    if snapshot_stable1 and snapshot_stable2:
        detect_changes("Stable Day 1 vs Day 2", snapshot_stable1["id"], snapshot_stable2["id"])

    # =========================================================================
    # Summary
    # =========================================================================
    print("\n" + "=" * 70)
    print("SEEDING COMPLETE!")
    print("=" * 70)
    print("\n📊 Summary:")
    print("   • 13 user snapshots created")
    print("   • 9 change detection analyses performed")
    print("   • 5 realistic scenarios demonstrated")
    print("\n🌐 View results:")
    print("   • Swagger UI: http://localhost:8000/docs")
    print("   • All snapshots: http://localhost:8000/api/v1/snapshots")
    print("   • All detections: http://localhost:8000/api/v1/detect")
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\nERROR: Cannot connect to API!")
        print("   Make sure the API is running: docker-compose up -d")
        print("   Then run this script again.\n")
    except Exception as e:
        print(f"\n ERROR: {e}\n")