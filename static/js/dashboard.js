document.addEventListener('DOMContentLoaded', () => {
    // Initialize dashboard
    fetchStats();
    fetchSuiteChart();
    fetchErrorChart();
    fetchFailures();

    // Setup search listener
    document.getElementById('searchInput').addEventListener('input', (e) => {
        fetchFailures(e.target.value);
    });
});

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

async function fetchSuiteChart() {
    try {
        const response = await fetch('/api/charts/suites');
        const data = await response.json();
        
        const labels = data.map(item => item.suite_name);
        const counts = data.map(item => item.count);
        
        const ctx = document.getElementById('suiteChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Failures',
                    data: counts,
                    backgroundColor: 'rgba(59, 130, 246, 0.8)',
                    borderColor: 'rgba(59, 130, 246, 1)',
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
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

async function fetchErrorChart() {
    try {
        const response = await fetch('/api/charts/errors');
        const data = await response.json();
        
        const labels = data.map(item => item.failure_type);
        const counts = data.map(item => item.count);
        
        const colors = [
            'rgba(239, 68, 68, 0.8)',   // red
            'rgba(245, 158, 11, 0.8)',  // yellow
            'rgba(16, 185, 129, 0.8)',  // green
            'rgba(139, 92, 246, 0.8)'   // purple
        ];

        const ctx = document.getElementById('errorChart').getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: counts,
                    backgroundColor: colors,
                    borderWidth: 1,
                    borderColor: '#1e293b'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
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

async function fetchFailures(searchQuery = '') {
    try {
        const url = `/api/failures${searchQuery ? `?search=${encodeURIComponent(searchQuery)}` : ''}`;
        const response = await fetch(url);
        const data = await response.json();
        
        const tbody = document.getElementById('failuresBody');
        tbody.innerHTML = '';
        
        if (data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" style="text-align:center">No failures found</td></tr>';
            return;
        }

        data.forEach(item => {
            const tr = document.createElement('tr');
            
            // Format date
            const date = new Date(item.execution_time);
            const formattedDate = date.toLocaleString();
            
            tr.innerHTML = `
                <td>${escapeHTML(item.test_name)}</td>
                <td><span style="background: rgba(255,255,255,0.1); padding: 4px 8px; border-radius: 4px; font-size: 0.85em">${escapeHTML(item.suite_name)}</span></td>
                <td>${escapeHTML(item.failure_type || 'Unknown')}</td>
                <td style="color: #94a3b8; font-size: 0.9em">${formattedDate}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error('Error fetching failures:', error);
    }
}

function escapeHTML(str) {
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
