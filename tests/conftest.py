import pytest
import sqlite3
import os
from app import app
from database import init_db

TEST_DB_PATH = 'test_results_test.db'

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['DATABASE'] = TEST_DB_PATH
    
    # Init DB with seed data for tests
    init_db(TEST_DB_PATH)
    
    with app.test_client() as client:
        yield client
        
    # Cleanup after tests
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
