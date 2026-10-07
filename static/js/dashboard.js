/* ─────────────────────────────────────────────────────────────────
   Test Failure Visualization Dashboard — dashboard.js
   Assessment-3: Failure Analysis & Filtering
───────────────────────────────────────────────────────────────── */

// ── Shared filter state ──────────────────────────────────────────
const filters = {
    suite: '',
    errorType: '',
    search: ''
};

// Chart instances (kept so we can re-highlight on filter)
let suiteChartInstance = null;
let errorChartInstance = null;

// ── Bootstrap ────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    fetchStats();
    fetchSuiteChart();
    fetchErrorChart();
    fetchAnalysis();
    fetchFailures();

    // Wire filter controls
    document.getElementById('suiteFilter').addEventListener('change', (e) => {
        filters.suite = e.target.value;
        applyFilters();
    });

    document.getElementById('errorTypeFilter').addEventListener('change', (e) => {
        filters.errorType = e.target.value;
        applyFilters();
    });

    document.getElementById('searchInput').addEventListener('input', (e) => {
        filters.search = e.target.value;
        applyFilters();
    });

    document.getElementById('clearFiltersBtn').addEventListener('click', () => {
        clearAllFilters();
    });
});

// ── Apply all active filters ─────────────────────────────────────
function applyFilters() {
    syncDropdownsToState();
    renderFilterChips();
    updateClearButton();
    fetchAnalysis();
    fetchFailures();
}

function clearAllFilters() {
    filters.suite = '';
    filters.errorType = '';
    filters.search = '';
    syncDropdownsToState();
    renderFilterChips();
    updateClearButton();
    fetchAnalysis();
    fetchFailures();
}

function syncDropdownsToState() {
    document.getElementById('suiteFilter').value = filters.suite;
    document.getElementById('errorTypeFilter').value = filters.errorType;
    document.getElementById('searchInput').value = filters.search;
}

function updateClearButton() {
    const hasFilter = filters.suite || filters.errorType || filters.search;
    document.getElementById('clearFiltersBtn').style.display = hasFilter ? 'inline-flex' : 'none';
}

// ── Filter chips ─────────────────────────────────────────────────
function renderFilterChips() {
    const container = document.getElementById('filterChips');
    container.innerHTML = '';
    if (filters.suite) {
        container.appendChild(createChip(`Suite: ${filters.suite}`, () => {
            filters.suite = '';
            applyFilters();
        }));
    }
    if (filters.errorType) {
        container.appendChild(createChip(`Error: ${filters.errorType}`, () => {
            filters.errorType = '';
            applyFilters();
        }));
    }
    if (filters.search) {
        container.appendChild(createChip(`Search: "${filters.search}"`, () => {
            filters.search = '';
            applyFilters();
        }));
    }
}

function createChip(label, onRemove) {
    const chip = document.createElement('div');
    chip.className = 'chip';
    chip.innerHTML = `<span>${escapeHTML(label)}</span><button title="Remove filter">✕</button>`;
    chip.querySelector('button').addEventListener('click', onRemove);
    return chip;
}

// ── Build query string from current filters ───────────────────────
function buildQuery(extras = {}) {
    const params = new URLSearchParams();
    const merged = { ...{ suite: filters.suite, error_type: filters.errorType, search: filters.search }, ...extras };
    for (const [k, v] of Object.entries(merged)) {
        if (v) params.set(k, v);
    }
    const qs = params.toString();
    return qs ? `?${qs}` : '';
}

// ── Stats (global — not filtered) ───────────────────────────────
async function fetchStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        document.getElementById('stat-total').textContent = data.TOTAL;
        document.getElementById('stat-passed').textContent = data.PASSED;
        document.getElementById('stat-failed').textContent = data.FAILED;
        document.getElementById('stat-skipped').textContent = data.SKIPPED;
        document.getElementById('stat-percentage').textContent = `${data.PASS_PERCENTAGE}%`;
    } catch (error) {
        console.error('Error fetching stats:', error);
    }
}

// ── Suite bar chart ──────────────────────────────────────────────
async function fetchSuiteChart() {
    try {
        const response = await fetch('/api/charts/suites');
        const data = await response.json();
        const labels = data.map(item => item.suite_name);
        const counts = data.map(item => item.count);

        const ctx = document.getElementById('suiteChart').getContext('2d');
        suiteChartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels,
                datasets: [{
                    label: 'Failures',
                    data: counts,
                    backgroundColor: labels.map(() => 'rgba(59, 130, 246, 0.8)'),
                    borderColor: labels.map(() => 'rgba(59, 130, 246, 1)'),
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                onClick: (evt, elements) => {
                    if (elements.length > 0) {
                        const idx = elements[0].index;
                        const clickedSuite = labels[idx];
                        filters.suite = filters.suite === clickedSuite ? '' : clickedSuite;
                        applyFilters();
                        highlightSuiteBar(idx, labels.length);
                    }
                },
                plugins: { legend: { display: false } },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        ticks: { color: '#94a3b8' }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: '#94a3b8' }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error fetching suite chart data:', error);
    }
}

function highlightSuiteBar(selectedIdx, total) {
    if (!suiteChartInstance) return;
    const ds = suiteChartInstance.data.datasets[0];
    ds.backgroundColor = ds.backgroundColor.map((_, i) =>
        i === selectedIdx && filters.suite
            ? 'rgba(59, 130, 246, 1)'
            : 'rgba(59, 130, 246, 0.35)'
    );
    suiteChartInstance.update();
    document.getElementById('suiteChart').closest('.chart-container')
        .classList.toggle('filter-active', !!filters.suite);
}

// ── Error-type doughnut chart ────────────────────────────────────
async function fetchErrorChart() {
    try {
        const response = await fetch('/api/charts/errors');
        const data = await response.json();
        const labels = data.map(item => item.failure_type);
        const counts = data.map(item => item.count);

        const palette = [
            'rgba(239, 68,  68,  0.85)',
            'rgba(245, 158, 11,  0.85)',
            'rgba(16,  185, 129, 0.85)',
            'rgba(139, 92,  246, 0.85)',
            'rgba(59,  130, 246, 0.85)'
        ];

        const ctx = document.getElementById('errorChart').getContext('2d');
        errorChartInstance = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels,
                datasets: [{
                    data: counts,
                    backgroundColor: palette.slice(0, labels.length),
                    borderWidth: 1,
                    borderColor: '#1e293b'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                onClick: (evt, elements) => {
                    if (elements.length > 0) {
                        const idx = elements[0].index;
                        const clickedType = labels[idx];
                        filters.errorType = filters.errorType === clickedType ? '' : clickedType;
                        applyFilters();
                        document.getElementById('errorChart').closest('.chart-container')
                            .classList.toggle('filter-active', !!filters.errorType);
                    }
                },
                plugins: {
                    legend: {
                        position: 'right',
                        labels: { color: '#f8fafc' }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error fetching error chart data:', error);
    }
}

// ── Failure Analysis panel ───────────────────────────────────────
async function fetchAnalysis() {
    try {
        const qs = buildQuery({ search: '' }); // analysis doesn't use keyword search
        const response = await fetch(`/api/analysis${qs}`);
        const data = await response.json();

        // Summary cards
        document.getElementById('analysis-total').textContent = data.total_failures;
        document.getElementById('analysis-suite').textContent = data.most_affected_suite || '—';
        document.getElementById('analysis-error').textContent = data.most_common_error || '—';

        // Populate dropdowns (only on first call — suites/error types are always global)
        populateDropdown('suiteFilter', data.available_suites, filters.suite);
        populateDropdown('errorTypeFilter', data.available_error_types, filters.errorType);

        // Breakdown table
        renderBreakdownTable(data.by_error_type);

    } catch (error) {
        console.error('Error fetching analysis:', error);
    }
}

function populateDropdown(id, options, currentValue) {
    const sel = document.getElementById(id);
    // Only rebuild if empty (don't reset while user is interacting after data is loaded)
    if (sel.options.length > 1) {
        sel.value = currentValue;
        return;
    }
    const placeholder = sel.options[0];
    sel.innerHTML = '';
    sel.appendChild(placeholder);
    options.forEach(opt => {
        const o = document.createElement('option');
        o.value = opt;
        o.textContent = opt;
        sel.appendChild(o);
    });
    sel.value = currentValue;
}

function renderBreakdownTable(byErrorType) {
    const tbody = document.getElementById('breakdownBody');
    tbody.innerHTML = '';

    if (!byErrorType || byErrorType.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;color:#94a3b8">No failure data for current filters</td></tr>';
        return;
    }

    byErrorType.forEach(item => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td style="font-family:monospace;color:var(--danger)">${escapeHTML(item.failure_type || 'Unknown')}</td>
            <td><strong>${item.count}</strong></td>
            <td>
                <div class="pct-bar-wrap">
                    <div class="pct-bar-bg">
                        <div class="pct-bar-fill" style="width:${item.percentage}%"></div>
                    </div>
                </div>
            </td>
            <td style="color:var(--text-muted)">${item.percentage}%</td>
        `;
        // Clicking a row filters by that error type
        tr.style.cursor = 'pointer';
        tr.title = `Filter by ${item.failure_type}`;
        tr.addEventListener('click', () => {
            filters.errorType = filters.errorType === item.failure_type ? '' : item.failure_type;
            applyFilters();
        });
        tbody.appendChild(tr);
    });
}

// ── Failures table ───────────────────────────────────────────────
async function fetchFailures() {
    try {
        const url = `/api/failures${buildQuery()}`;
        const response = await fetch(url);
        const data = await response.json();

        const tbody = document.getElementById('failuresBody');
        const countEl = document.getElementById('resultCount');
        tbody.innerHTML = '';

        countEl.textContent = data.length > 0 ? `(${data.length} result${data.length !== 1 ? 's' : ''})` : '';

        if (data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:#94a3b8">No failures match the current filters</td></tr>';
            return;
        }

        data.forEach(item => {
            const tr = document.createElement('tr');
            const date = new Date(item.execution_time);
            const formattedDate = isNaN(date) ? item.execution_time : date.toLocaleString();

            tr.innerHTML = `
                <td>${escapeHTML(item.test_name)}</td>
                <td><span class="suite-tag">${escapeHTML(item.suite_name)}</span></td>
                <td>${escapeHTML(item.failure_type || 'Unknown')}</td>
                <td>${item.duration_ms ?? '—'}</td>
                <td style="color:#94a3b8;font-size:0.9em">${formattedDate}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error('Error fetching failures:', error);
    }
}

// ── Utility ──────────────────────────────────────────────────────
function escapeHTML(str) {
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}
