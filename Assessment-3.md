# Assessment 3: Feature Implementation

## Project Title
Test Failure Visualization Dashboard

## Feature Implemented: Failure Analysis & Filtering

### Overview
Assessment-3 adds an end-to-end **Failure Analysis Panel** that allows users to drill deeply into failing tests using a set of combinable, real-time filters. It transforms the dashboard from a static summary into an interactive diagnostic tool.

---

## Feature Components

### 1. New Backend Endpoint — `GET /api/analysis`
Returns a structured failure analysis object:
- `total_failures` — total failing tests matching the active filters.
- `most_affected_suite` — the suite with the highest failure count.
- `most_common_error` — the most frequently occurring error type.
- `by_error_type[]` — list of error types with count and percentage of failures.
- `by_suite[]` — list of suites with count and percentage of failures.
- `available_suites[]` and `available_error_types[]` — data for populating dropdowns.
- `active_filters` — echoes the filters applied.

**Optional query parameters:**
- `?suite=<suite_name>` — restrict analysis to one test suite.
- `?error_type=<failure_type>` — restrict analysis to one error type.

### 2. Enhanced `GET /api/failures`
Now accepts three independent, combinable parameters:
- `?search=<keyword>` — keyword search across test name, suite, and error type (original).
- `?suite=<suite_name>` — exact suite filter (new).
- `?error_type=<failure_type>` — exact error type filter (new).

### 3. Failure Analysis UI Panel
A new section displayed between the Chart.js charts and the failures table, containing:
- **Filter Bar** — Suite dropdown, Error Type dropdown, and keyword search input, wired together to update the analysis and table simultaneously.
- **Active Filter Chips** — clickable chips that appear when any filter is active, with an individual ✕ button and a global "Clear Filters" button.
- **Analysis Summary Cards** — three mini-cards for Total Failures, Most Affected Suite, and Most Common Error.
- **Error Breakdown Table** — shows each error type with count, a visual percentage bar, and percentage value. Clicking a row applies that error type as a filter.

### 4. Chart Click Filtering
- **Bar chart (Failures by Suite):** Clicking a bar sets the suite filter. Clicking again deactivates it. Active bars are visually highlighted.
- **Doughnut chart (Failures by Type):** Clicking a segment sets the error type filter.

### 5. Updated Failures Table
- Now also shows `duration_ms` column.
- Displays a result count (e.g. "12 results").
- "No failures match the current filters" when the filtered result is empty.

---

## Architecture Changes

| Layer | Change |
|---|---|
| **Flask (`app.py`)** | Added `GET /api/analysis`; extended `GET /api/failures` with `suite` and `error_type` params |
| **Frontend HTML (`index.html`)** | Added Failure Analysis section with filter bar, chips, summary cards, breakdown table |
| **CSS (`style.css`)** | Added styles for filter bar, chips, analysis cards, breakdown table, percentage bars, chart active state |
| **JavaScript (`dashboard.js`)** | Shared filter state object; unified `applyFilters()` function; chart click handlers; analysis + dropdown population |
| **Tests (`tests/test_api.py`)** | +12 new tests for all new functionality (5 original tests preserved) |

---

## Testing Performed

### Automated Tests
All 17 tests pass:
```
tests/test_api.py::test_stats_endpoint PASSED
tests/test_api.py::test_charts_suites_endpoint PASSED
tests/test_api.py::test_charts_errors_endpoint PASSED
tests/test_api.py::test_recent_failures_endpoint_no_search PASSED
tests/test_api.py::test_recent_failures_endpoint_with_search PASSED
tests/test_api.py::test_analysis_endpoint_structure PASSED
tests/test_api.py::test_analysis_total_matches_failures PASSED
tests/test_api.py::test_analysis_most_affected_suite_valid PASSED
tests/test_api.py::test_analysis_most_common_error_valid PASSED
tests/test_api.py::test_analysis_percentages_sum_to_100 PASSED
tests/test_api.py::test_analysis_filter_by_suite PASSED
tests/test_api.py::test_analysis_filter_by_error_type PASSED
tests/test_api.py::test_analysis_combined_filters PASSED
tests/test_api.py::test_failures_filter_by_suite PASSED
tests/test_api.py::test_failures_filter_by_error_type PASSED
tests/test_api.py::test_failures_combined_filters PASSED
tests/test_api.py::test_failures_duration_field_present PASSED
17 passed in 0.44s
```

### Manual Verification
- Dashboard loads correctly with the new Failure Analysis Panel visible.
- Suite dropdown filters both the analysis summary and the failures table.
- Error Type dropdown filters both the breakdown table and the failures table.
- Keyword search works in combination with suite and error-type filters.
- Clicking a suite bar in the chart sets the Suite dropdown and triggers a re-fetch.
- Clicking a doughnut segment sets the Error Type dropdown and triggers a re-fetch.
- Filter chips appear correctly for each active filter and can be individually removed.
- "Clear Filters" button resets all three filters simultaneously.
- Existing top-level stats and chart data are unaffected by the analysis filters.

---

## Users/Stakeholders Served
- **QA Engineers:** Can now drill down into a specific module (e.g., PaymentGateway) to see its most common failure pattern.
- **Developers:** Can quickly isolate all AssertionError failures across all suites in one click.
- **Engineering Managers:** The analysis panel gives an instant at-a-glance breakdown of the most problematic areas.
