# Test Failure Visualization Dashboard

A lightweight, elegant web dashboard for visualizing automated test execution results and failures. Built entirely with Python (Flask) on the backend and pure Vanilla HTML/CSS/JS on the frontend.

## ✨ Features
- **Dashboard UI:** A comprehensive single-page dashboard displaying key test execution metrics.
- **Top-Level Metrics:** Tracks Total, Passed, Failed, and Skipped tests, alongside Pass Percentage.
- **Dynamic Charts:** Visualizes failure distribution across different test suites and failure types using Chart.js.
- **Recent Failures Table:** A searchable tabular view to quickly identify recent failing tests and their details.
- **Automated Mock Data:** Self-initializing SQLite database populated with realistic synthetic test data.

## 🏗️ Architecture/Structure
The project follows a classic, lightweight Client-Server architecture:
- **Backend (Python/Flask):** Provides RESTful API endpoints (`/api/stats`, `/api/charts/*`, `/api/failures`) and serves the frontend.
- **Database (SQLite):** Stores persistent test results using the native `sqlite3` module.
- **Frontend (Vanilla HTML/CSS/JS):** A zero-dependency (aside from Chart.js CDN) presentation layer utilizing modern CSS design principles (glassmorphism, dark mode).

```text
test-failure-dashboard/
├── app.py                 # Main Flask application and REST endpoints
├── database.py            # SQLite initialization and dummy data seeding
├── requirements.txt       # Python dependencies
├── static/                # Vanilla CSS styles and JavaScript logic
├── templates/             # HTML dashboard layout
└── tests/                 # Pytest automated unit tests
```

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8+

### Installation

1. Navigate to the project directory:
```bash
cd test-failure-dashboard
```

2. Create a virtual environment and activate it:
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```
*(Note: The application will automatically initialize the SQLite database and seed it with 150 realistic test result records on the first run).*

5. Open your browser and navigate to `http://localhost:5000`

### Running Unit Tests
To run the automated test suite, ensure your virtual environment is active and run:
```bash
pytest
```

## 🧠 Learnings

During the development of this first deliverable, several key learnings were identified:
- **Separation of Concerns:** By strictly isolating the project from existing code, we ensure a clean namespace and prevent dependency conflicts (e.g., between different versions of FastAPI and Flask).
- **Vanilla Aesthetics:** High-quality, modern UI designs (dark mode, glassmorphism, micro-animations) can be achieved entirely without heavy frontend frameworks like React or Tailwind, keeping the bundle size near zero.
- **In-Memory Testing:** Using an isolated test database (and cleaning it up post-run via Pytest fixtures) ensures that unit tests run fast and do not mutate the production/development database.
- **Native SQL:** Utilizing Python's built-in `sqlite3` module simplifies the stack drastically by removing the need for ORM configuration (like SQLAlchemy) for straightforward queries.
