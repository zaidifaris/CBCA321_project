# Assessment 2: Project Specification

## 1. Project Title and Description
**Title:** Test Failure Visualization Dashboard
**Description:** A web-based application designed to visualize automated software test failures. It ingests test execution data and presents actionable metrics, such as overall pass/fail percentages, and detailed breakdowns of failing tests by test suite and error type. This helps engineering teams quickly identify and resolve regressions and flaky tests.

## 2. Major Components
- **UI:** A frontend dashboard displaying statistics and interactive charts (Chart.js) built using HTML, Vanilla CSS, and JavaScript.
- **Data/Persistence:** A SQLite database to persist historical test runs and failure records.
- **Logic:** A Python Flask backend that serves as an API to compute statistical aggregates, handle filtering, and serve the data to the frontend.

## 3. Architecture
The system employs a classic client-server architecture:
- **Client:** The user's web browser, rendering HTML/CSS and using AJAX to fetch dynamic chart data from the backend.
- **Server:** A Flask RESTful API processing requests, querying the database, and responding with JSON payloads.
- **Database:** A local SQLite relational database (`test_results.db`) containing a schema optimized for querying test statuses and failure categorization.

## 4. Minimal Features for the First Deliverable
- **Day 1:** Implement the foundational database schema and dummy data seeder.
- **Day 2:** Develop the core Flask backend API endpoints (Stats, Chart Data).
- **Day 3:** Build the frontend UI layout (Stat Cards and Table) with Vanilla CSS styling.
- **Day 4:** Integrate Chart.js visualizations and wire up the Search/Filter logic for the failures table.

## 5. Users/Stakeholders
- **QA Engineers:** Monitor automated test stability and track long-term flaky tests.
- **Developers:** Use the dashboard to quickly isolate the root cause of CI failures via the failure type breakdown.
- **Engineering Managers:** Track the overall health and pass percentage of the test suite over time.

## 6. Components of First Deliverable
1. SQLite database initialization and seeding script (`database.py`).
2. Flask web server and API (`app.py`).
3. Frontend Dashboard UI (`index.html`, `style.css`, `dashboard.js`).
4. Automated unit tests for backend API (`tests/`).
5. Project documentation and README.

## 7. Interfaces of Components
- **Web Interface:** Interactive browser-based UI for users.
- **Internal REST API:**
  - `GET /api/stats` (Returns aggregate test counts)
  - `GET /api/charts/suites` (Returns failures grouped by suite)
  - `GET /api/charts/errors` (Returns failures grouped by error type)
  - `GET /api/failures` (Returns tabular failure data with optional `?search=` parameter)

## 8. Technology Stack
- **Backend:** Python 3, Flask
- **Frontend:** HTML5, CSS3 (Vanilla), JavaScript (Vanilla)
- **Visualizations:** Chart.js
- **Database:** SQLite (built-in `sqlite3` module)
- **Testing:** Pytest, pytest-flask
