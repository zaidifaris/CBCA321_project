import sqlite3
import random
from datetime import datetime, timedelta

DB_PATH = 'test_results.db'

def get_db_connection(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path=DB_PATH):
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    # Drop existing table if exists (for resetting data)
    cursor.execute('DROP TABLE IF EXISTS test_results')

    # Create table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_name TEXT NOT NULL,
            suite_name TEXT NOT NULL,
            status TEXT NOT NULL,
            failure_type TEXT,
            duration_ms INTEGER,
            execution_time TIMESTAMP
        )
    ''')

    # Seed with sample data
    suites = ['AuthModule', 'PaymentGateway', 'UserDashboard', 'ReportingService']
    statuses = ['PASSED', 'FAILED', 'SKIPPED']
    failure_types = ['AssertionError', 'TimeoutException', 'NullReferenceException', 'NetworkError', None]

    now = datetime.now()
    records = []

    for i in range(150):
        suite = random.choice(suites)
        # Weighting the statuses (80% pass, 15% fail, 5% skip)
        status = random.choices(statuses, weights=[0.8, 0.15, 0.05], k=1)[0]
        
        test_name = f'test_{suite.lower()}_{i}'
        duration = random.randint(10, 500)
        execution_time = now - timedelta(hours=random.randint(0, 48), minutes=random.randint(0, 59))
        
        failure_type = None
        if status == 'FAILED':
            failure_type = random.choice([ft for ft in failure_types if ft is not None])

        records.append((test_name, suite, status, failure_type, duration, str(execution_time)))

    cursor.executemany('''
        INSERT INTO test_results (test_name, suite_name, status, failure_type, duration_ms, execution_time)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', records)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized and seeded.")
