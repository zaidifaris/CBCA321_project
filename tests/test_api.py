KNOWN_SUITES = {'AuthModule', 'PaymentGateway', 'UserDashboard', 'ReportingService'}
KNOWN_ERROR_TYPES = {'AssertionError', 'TimeoutException', 'NullReferenceException', 'NetworkError'}

# ──────────────────────────────────────────────────────────
# Original Assessment-2 tests (preserved, unchanged)
# ──────────────────────────────────────────────────────────

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
    response = client.get('/api/failures?search=AuthModule')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)

# ──────────────────────────────────────────────────────────
# Assessment-3 tests — /api/analysis
# ──────────────────────────────────────────────────────────

def test_analysis_endpoint_structure(client):
    """Response must contain all required top-level keys."""
    response = client.get('/api/analysis')
    assert response.status_code == 200
    data = response.get_json()

    required_keys = [
        'total_failures',
        'most_affected_suite',
        'most_common_error',
        'by_error_type',
        'by_suite',
        'available_suites',
        'available_error_types',
        'active_filters',
    ]
    for key in required_keys:
        assert key in data, f"Missing key: {key}"

def test_analysis_total_matches_failures(client):
    """total_failures must equal the number of FAILED rows seeded (probabilistic but reliable)."""
    stats = client.get('/api/stats').get_json()
    analysis = client.get('/api/analysis').get_json()
    assert analysis['total_failures'] == stats['FAILED']

def test_analysis_most_affected_suite_valid(client):
    """most_affected_suite must be one of the known seeded suites."""
    data = client.get('/api/analysis').get_json()
    assert data['most_affected_suite'] in KNOWN_SUITES

def test_analysis_most_common_error_valid(client):
    """most_common_error must be one of the known seeded error types."""
    data = client.get('/api/analysis').get_json()
    assert data['most_common_error'] in KNOWN_ERROR_TYPES

def test_analysis_percentages_sum_to_100(client):
    """Sum of by_error_type percentages must be approximately 100."""
    data = client.get('/api/analysis').get_json()
    total_pct = sum(item['percentage'] for item in data['by_error_type'])
    assert abs(total_pct - 100.0) < 1.0, f"Percentages summed to {total_pct}, expected ~100"

def test_analysis_filter_by_suite(client):
    """?suite= filter must restrict by_suite to only the requested suite."""
    data = client.get('/api/analysis?suite=AuthModule').get_json()
    assert data['active_filters']['suite'] == 'AuthModule'
    for item in data['by_suite']:
        assert item['suite_name'] == 'AuthModule'
    # All failures counted must belong to AuthModule
    for item in data['by_error_type']:
        assert item['count'] >= 0  # counts are non-negative

def test_analysis_filter_by_error_type(client):
    """?error_type= filter must restrict by_error_type to only that error type."""
    data = client.get('/api/analysis?error_type=AssertionError').get_json()
    assert data['active_filters']['error_type'] == 'AssertionError'
    for item in data['by_error_type']:
        assert item['failure_type'] == 'AssertionError'

def test_analysis_combined_filters_suite_and_error_type(client):
    """
    BUG REGRESSION: When both suite and error_type filters are active,
    most_affected_suite and most_common_error must both reflect the combined
    filtered dataset — not a partially-filtered one.
    With suite=PaymentGateway&error_type=AssertionError, every failure in the
    result belongs to PaymentGateway AND is an AssertionError, so:
      - most_affected_suite must be PaymentGateway (the only suite in the set)
      - most_common_error must be AssertionError (the only error type in the set)
    """
    data = client.get('/api/analysis?suite=PaymentGateway&error_type=AssertionError').get_json()
    # All by_suite entries must be PaymentGateway
    for item in data['by_suite']:
        assert item['suite_name'] == 'PaymentGateway'
    # All by_error_type entries must be AssertionError
    for item in data['by_error_type']:
        assert item['failure_type'] == 'AssertionError'
    # Summary cards must also reflect the filtered data
    if data['total_failures'] > 0:
        assert data['most_affected_suite'] == 'PaymentGateway', (
            f"Expected most_affected_suite='PaymentGateway', got '{data['most_affected_suite']}'"
        )
        assert data['most_common_error'] == 'AssertionError', (
            f"Expected most_common_error='AssertionError', got '{data['most_common_error']}'"
        )

def test_analysis_combined_filters_authmodule_and_assertion(client):
    """
    BUG REGRESSION: suite=AuthModule&error_type=AssertionError must also constrain
    most_affected_suite to AuthModule and most_common_error to AssertionError.
    """
    data = client.get('/api/analysis?suite=AuthModule&error_type=AssertionError').get_json()
    for item in data['by_suite']:
        assert item['suite_name'] == 'AuthModule'
    for item in data['by_error_type']:
        assert item['failure_type'] == 'AssertionError'
    if data['total_failures'] > 0:
        assert data['most_affected_suite'] == 'AuthModule', (
            f"Expected most_affected_suite='AuthModule', got '{data['most_affected_suite']}'"
        )
        assert data['most_common_error'] == 'AssertionError', (
            f"Expected most_common_error='AssertionError', got '{data['most_common_error']}'"
        )

def test_analysis_filter_suite_only_constrains_most_common_error(client):
    """
    BUG REGRESSION: ?suite=PaymentGateway alone — most_common_error must be
    calculated from PaymentGateway failures only, not globally.
    """
    data = client.get('/api/analysis?suite=PaymentGateway').get_json()
    assert data['active_filters']['suite'] == 'PaymentGateway'
    # most_affected_suite must be PaymentGateway (the only suite in filtered set)
    if data['total_failures'] > 0:
        assert data['most_affected_suite'] == 'PaymentGateway', (
            f"Expected most_affected_suite='PaymentGateway', got '{data['most_affected_suite']}'"
        )
    # most_common_error must come from by_error_type[0] which is derived from filtered data
    if data['by_error_type']:
        assert data['most_common_error'] == data['by_error_type'][0]['failure_type'], (
            "most_common_error does not match the top entry in by_error_type"
        )

def test_analysis_filter_error_type_only_constrains_most_affected_suite(client):
    """
    BUG REGRESSION: ?error_type=AssertionError alone — most_affected_suite must be
    calculated from AssertionError failures only, not globally.
    """
    data = client.get('/api/analysis?error_type=AssertionError').get_json()
    assert data['active_filters']['error_type'] == 'AssertionError'
    # most_common_error must be AssertionError (the only error type in filtered set)
    if data['total_failures'] > 0:
        assert data['most_common_error'] == 'AssertionError', (
            f"Expected most_common_error='AssertionError', got '{data['most_common_error']}'"
        )
    # most_affected_suite must come from by_suite[0] which is derived from filtered data
    if data['by_suite']:
        assert data['most_affected_suite'] == data['by_suite'][0]['suite_name'], (
            "most_affected_suite does not match the top entry in by_suite"
        )

def test_analysis_summary_always_consistent_with_breakdowns(client):
    """
    Structural invariant: most_affected_suite and most_common_error must ALWAYS
    equal by_suite[0]['suite_name'] and by_error_type[0]['failure_type'] respectively,
    regardless of what filters are active. Tested for all four filter combos.
    """
    combos = [
        '/api/analysis',
        '/api/analysis?suite=PaymentGateway',
        '/api/analysis?error_type=AssertionError',
        '/api/analysis?suite=PaymentGateway&error_type=AssertionError',
    ]
    for url in combos:
        data = client.get(url).get_json()
        if data['by_suite']:
            assert data['most_affected_suite'] == data['by_suite'][0]['suite_name'], (
                f"Inconsistency at {url}: most_affected_suite='{data['most_affected_suite']}' "
                f"but by_suite[0]='{data['by_suite'][0]['suite_name']}'"
            )
        if data['by_error_type']:
            assert data['most_common_error'] == data['by_error_type'][0]['failure_type'], (
                f"Inconsistency at {url}: most_common_error='{data['most_common_error']}' "
                f"but by_error_type[0]='{data['by_error_type'][0]['failure_type']}'"
            )


# ──────────────────────────────────────────────────────────
# Assessment-3 tests — enhanced /api/failures filters
# ──────────────────────────────────────────────────────────

def test_failures_filter_by_suite(client):
    """?suite= must return only failures from that suite."""
    response = client.get('/api/failures?suite=AuthModule')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    for item in data:
        assert item['suite_name'] == 'AuthModule'

def test_failures_filter_by_error_type(client):
    """?error_type= must return only failures of that error type."""
    response = client.get('/api/failures?error_type=TimeoutException')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    for item in data:
        assert item['failure_type'] == 'TimeoutException'

def test_failures_combined_filters(client):
    """?suite= + ?error_type= must apply both constraints simultaneously."""
    response = client.get('/api/failures?suite=PaymentGateway&error_type=NetworkError')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    for item in data:
        assert item['suite_name'] == 'PaymentGateway'
        assert item['failure_type'] == 'NetworkError'

def test_failures_duration_field_present(client):
    """Updated /api/failures must include duration_ms in the response."""
    response = client.get('/api/failures')
    assert response.status_code == 200
    data = response.get_json()
    if len(data) > 0:
        assert 'duration_ms' in data[0]
