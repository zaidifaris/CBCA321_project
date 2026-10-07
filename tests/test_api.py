def test_stats_endpoint(client):
    response = client.get('/api/stats')
    assert response.status_code == 200
    data = response.get_json()
    
    assert 'TOTAL' in data
    assert 'PASSED' in data
    assert 'FAILED' in data
    assert 'SKIPPED' in data
    assert 'PASS_PERCENTAGE' in data
    
    # Ensure math is right
    assert data['TOTAL'] == data['PASSED'] + data['FAILED'] + data['SKIPPED']
    assert data['TOTAL'] == 150  # We seed 150 records

def test_charts_suites_endpoint(client):
    response = client.get('/api/charts/suites')
    assert response.status_code == 200
    data = response.get_json()
    
    assert isinstance(data, list)
    if len(data) > 0:
        assert 'suite_name' in data[0]
        assert 'count' in data[0]

def test_charts_errors_endpoint(client):
    response = client.get('/api/charts/errors')
    assert response.status_code == 200
    data = response.get_json()
    
    assert isinstance(data, list)
    if len(data) > 0:
        assert 'failure_type' in data[0]
        assert 'count' in data[0]

def test_recent_failures_endpoint_no_search(client):
    response = client.get('/api/failures')
    assert response.status_code == 200
    data = response.get_json()
    
    assert isinstance(data, list)
    if len(data) > 0:
        assert 'test_name' in data[0]
        assert 'suite_name' in data[0]
        assert 'failure_type' in data[0]

def test_recent_failures_endpoint_with_search(client):
    # This assumes that 'AuthModule' will likely have at least one failure given 150 rows.
    # If it flakes, we can search for a very broad term, but this is just testing the endpoint handles args.
    response = client.get('/api/failures?search=AuthModule')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
