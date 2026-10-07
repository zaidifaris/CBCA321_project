from flask import Flask, jsonify, request, render_template
import sqlite3
from database import get_db_connection, init_db, DB_PATH
import os

app = Flask(__name__)

# Initialize DB if it doesn't exist
if not os.path.exists(DB_PATH) and not os.environ.get("TESTING"):
    init_db(DB_PATH)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats', methods=['GET'])
def get_stats():
    conn = get_db_connection(app.config.get("DATABASE", DB_PATH))
    cursor = conn.cursor()
    
    cursor.execute("SELECT status, COUNT(*) as count FROM test_results GROUP BY status")
    rows = cursor.fetchall()
    conn.close()
    
    stats = {'TOTAL': 0, 'PASSED': 0, 'FAILED': 0, 'SKIPPED': 0}
    for row in rows:
        stats[row['status']] = row['count']
        stats['TOTAL'] += row['count']
        
    stats['PASS_PERCENTAGE'] = round((stats['PASSED'] / stats['TOTAL']) * 100, 2) if stats['TOTAL'] > 0 else 0
    return jsonify(stats)

@app.route('/api/charts/suites', methods=['GET'])
def get_suite_failures():
    conn = get_db_connection(app.config.get("DATABASE", DB_PATH))
    cursor = conn.cursor()
    
    cursor.execute("SELECT suite_name, COUNT(*) as count FROM test_results WHERE status = 'FAILED' GROUP BY suite_name")
    rows = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(row) for row in rows])

@app.route('/api/charts/errors', methods=['GET'])
def get_error_types():
    conn = get_db_connection(app.config.get("DATABASE", DB_PATH))
    cursor = conn.cursor()
    
    cursor.execute("SELECT failure_type, COUNT(*) as count FROM test_results WHERE status = 'FAILED' GROUP BY failure_type")
    rows = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(row) for row in rows])

@app.route('/api/analysis', methods=['GET'])
def get_analysis():
    """
    Returns a structured failure analysis summary.
    Optional query params:
        ?suite=<suite_name>        — filter to a specific test suite
        ?error_type=<failure_type> — filter to a specific failure type
    """
    suite_filter = request.args.get('suite', '')
    error_type_filter = request.args.get('error_type', '')

    db_path = app.config.get("DATABASE", DB_PATH)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    # Build the base WHERE clause
    base_conditions = ["status = 'FAILED'"]
    base_params = []
    if suite_filter:
        base_conditions.append("suite_name = ?")
        base_params.append(suite_filter)
    if error_type_filter:
        base_conditions.append("failure_type = ?")
        base_params.append(error_type_filter)
    where_clause = " AND ".join(base_conditions)

    # Total failures (with all filters applied)
    cursor.execute(f"SELECT COUNT(*) as total FROM test_results WHERE {where_clause}", base_params)
    total_failures = cursor.fetchone()['total']

    # Breakdown by error type — respects all active filters
    cursor.execute(
        f"SELECT failure_type, COUNT(*) as count FROM test_results WHERE {where_clause} "
        f"GROUP BY failure_type ORDER BY count DESC",
        base_params
    )
    error_rows = cursor.fetchall()
    by_error_type = []
    for row in error_rows:
        pct = round((row['count'] / total_failures) * 100, 1) if total_failures > 0 else 0
        by_error_type.append({
            'failure_type': row['failure_type'],
            'count': row['count'],
            'percentage': pct
        })

    # Breakdown by suite — respects all active filters
    cursor.execute(
        f"SELECT suite_name, COUNT(*) as count FROM test_results WHERE {where_clause} "
        f"GROUP BY suite_name ORDER BY count DESC",
        base_params
    )
    suite_rows = cursor.fetchall()
    by_suite = []
    for row in suite_rows:
        pct = round((row['count'] / total_failures) * 100, 1) if total_failures > 0 else 0
        by_suite.append({
            'suite_name': row['suite_name'],
            'count': row['count'],
            'percentage': pct
        })

    # Derive summary values from the already-filtered breakdowns (guaranteed consistent)
    most_affected_suite = by_suite[0]['suite_name'] if by_suite else None
    most_common_error   = by_error_type[0]['failure_type'] if by_error_type else None


    # Available suites and error types for populating dropdowns
    cursor.execute("SELECT DISTINCT suite_name FROM test_results WHERE status = 'FAILED' ORDER BY suite_name")
    available_suites = [row['suite_name'] for row in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT failure_type FROM test_results WHERE status = 'FAILED' ORDER BY failure_type")
    available_error_types = [row['failure_type'] for row in cursor.fetchall()]

    conn.close()

    return jsonify({
        'total_failures': total_failures,
        'most_affected_suite': most_affected_suite,
        'most_common_error': most_common_error,
        'by_error_type': by_error_type,
        'by_suite': by_suite,
        'available_suites': available_suites,
        'available_error_types': available_error_types,
        'active_filters': {
            'suite': suite_filter,
            'error_type': error_type_filter
        }
    })

@app.route('/api/failures', methods=['GET'])
def get_recent_failures():
    """
    Returns a list of recent failed tests.
    Optional query params:
        ?search=<keyword>          — keyword search across test_name, suite_name, failure_type
        ?suite=<suite_name>        — filter by exact suite name
        ?error_type=<failure_type> — filter by exact failure type
    """
    search = request.args.get('search', '')
    suite_filter = request.args.get('suite', '')
    error_type_filter = request.args.get('error_type', '')

    conn = get_db_connection(app.config.get("DATABASE", DB_PATH))
    cursor = conn.cursor()
    
    query = """
        SELECT test_name, suite_name, failure_type, duration_ms, execution_time 
        FROM test_results 
        WHERE status = 'FAILED'
    """
    params = []

    if search:
        query += " AND (test_name LIKE ? OR suite_name LIKE ? OR failure_type LIKE ?)"
        like_search = f"%{search}%"
        params.extend([like_search, like_search, like_search])

    if suite_filter:
        query += " AND suite_name = ?"
        params.append(suite_filter)

    if error_type_filter:
        query += " AND failure_type = ?"
        params.append(error_type_filter)

    query += " ORDER BY execution_time DESC LIMIT 50"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(row) for row in rows])

if __name__ == '__main__':
    app.run(debug=True, port=5000)
