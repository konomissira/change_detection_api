# Change Detection API

A FastAPI-based service for detecting changes between user snapshots using set operations to identify new users, churned users, and retained users.

## Project Overview

This project demonstrates efficient change detection techniques for comparing user snapshots over time (daily, weekly, monthly) using set intersection and difference operations.

**Real-World Scenario:**

-   Yesterday: 10,000 active users
-   Today: 10,250 active users
-   **Who's new? Who churned? Who stayed?**

## Features

-   Compare user snapshots from different time periods
-   Find new users using SET DIFFERENCE (today - yesterday)
-   Find churned users using SET DIFFERENCE (yesterday - today)
-   Find retained users using SET INTERSECTION
-   Calculate growth rate, churn rate, retention rate
-   Track historical snapshots
-   REST API for automated change detection
-   PostgreSQL database for snapshot tracking
-   Docker containerization for easy deployment
-   Comprehensive API documentation

## Use Cases

-   User growth/churn analysis
-   Active user tracking
-   Customer retention monitoring
-   Subscriber changes
-   Daily/weekly/monthly user activity comparison
-   Product engagement tracking
-   SaaS metrics monitoring

## Tech Stack

-   **Python 3.11**
-   **FastAPI** - Modern web framework
-   **PostgreSQL** - Database
-   **SQLAlchemy** - ORM
-   **Docker & Docker Compose** - Containerization
-   **pytest** - Testing

## Project Status

🚧 **In Development** - This project is being built incrementally with proper Git workflow.

## Coming Soon

-   Installation instructions
-   Usage examples
-   API documentation
-   Contributing guidelines

## Author

Built as part of a data engineering portfolio project - **Project 4 of 4** in the Data Structures & Algorithms series.

## License

MIT License
