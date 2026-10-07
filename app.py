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

@app.route('/api/failures', methods=['GET'])
def get_recent_failures():
    search = request.args.get('search', '')
    conn = get_db_connection(app.config.get("DATABASE", DB_PATH))
    cursor = conn.cursor()
    
    query = """
        SELECT test_name, suite_name, failure_type, execution_time 
        FROM test_results 
        WHERE status = 'FAILED'
    """
    params = []
    
    if search:
        query += " AND (test_name LIKE ? OR suite_name LIKE ? OR failure_type LIKE ?)"
        like_search = f"%{search}%"
        params.extend([like_search, like_search, like_search])
        
    query += " ORDER BY execution_time DESC LIMIT 50"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(row) for row in rows])

if __name__ == '__main__':
    app.run(debug=True, port=5000)
