function initDashboardPage() {
  if (!requireAuth()) return;
  const user = getUserInfo();
  document.title = user.role === 'Admin' ? 'Admin Dashboard | SQL Migrator' : 'Dashboard | SQL Migrator';
  loadSharedComponent('header', () => {
    setProfileSummary();
    bindHeaderActions();
  });
  initSidebar();
  const headerTitle = document.getElementById('page-title');
  if (headerTitle) {
    headerTitle.textContent = user.role === 'Admin' ? 'Admin Dashboard' : 'User Dashboard';
  }

  injectQuickActions();
  loadDashboardData(user);
}

async function loadDashboardData(user) {
  const [historyRes, adminRes] = await Promise.all([
    apiRequest('/history', 'GET'),
    user.role === 'Admin' ? apiRequest('/admin/stats', 'GET') : Promise.resolve(null),
  ]);

  const history = historyRes.history || [];
  const adminStats = adminRes || {};

  renderSummary(history, adminStats);
  renderRecentActivity(history);
  renderDashboardCharts(history, adminStats);
}

function renderSummary(history, adminStats) {
  const total = history.length;
  const successful = history.filter((r) => r.status === 'completed').length;
  const failed = history.filter((r) => r.status === 'failed').length;
  const reports = history.filter((r) => r.report_summary).length;

  const summaryContainer = document.getElementById('dashboard-summary');
  if (!summaryContainer) return;
  summaryContainer.innerHTML = `
    <div class="card metric-card"><h3>Total Migrations</h3><strong>${total}</strong></div>
    <div class="card metric-card"><h3>Successful</h3><strong>${successful}</strong></div>
    <div class="card metric-card"><h3>Failed</h3><strong>${failed}</strong></div>
    <div class="card metric-card"><h3>Reports Generated</h3><strong>${reports}</strong></div>
  `;
}

function renderRecentActivity(history) {
  const activityContainer = document.getElementById('recent-activity');
  if (!activityContainer) return;

  const recent = history.slice(0, 5);
  if (recent.length === 0) {
    activityContainer.innerHTML = '<p class="small-text">No recent activity.</p>';
    return;
  }

  activityContainer.innerHTML = recent
    .map((record) => {
      const actionMap = {
        sql_to_sql: 'Completed SQL to SQL migration',
        tabular: 'Imported file to database',
        sql_dump: 'Imported SQL dump',
        file_import: 'Imported file to database',
      };
      const action = actionMap[record.migration_type] || `Migration: ${record.migration_type}`;
      const date = record.timestamp ? new Date(record.timestamp).toLocaleString() : '—';
      const statusClass = record.status === 'completed' ? 'status-success' : 'status-error';
      return `
        <div class="activity-item">
          <div>
            <strong>${record.source_db || 'Unknown source'}</strong>
            <p class="small-text">${action} → ${record.target_db || '—'}</p>
          </div>
          <span class="small-text">${date}</span>
          <span class="status-pill ${statusClass}">${record.status}</span>
        </div>
      `;
    })
    .join('');
}

function injectQuickActions() {
  const quickActions = document.getElementById('quick-actions');
  if (!quickActions) return;
  quickActions.innerHTML = `
    <button class="button-primary" onclick="window.location.href='../pages/migration.html'">New Migration</button>
    <button class="button-secondary" onclick="window.location.href='../pages/migration_history.html'">View History</button>
    <button class="button-secondary" onclick="window.location.href='../pages/reports.html'">Generate Report</button>
  `;
}

function renderDashboardCharts(history, adminStats) {
  if (!window.Chart) return;

  // --- Migration trends: last 7 days ---
  const trends = document.getElementById('migration-trends-chart');
  if (trends) {
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const counts = Array(7).fill(0);
    const now = new Date();
    history.forEach((r) => {
      if (!r.timestamp) return;
      const d = new Date(r.timestamp);
      const diffDays = Math.floor((now - d) / 86400000);
      if (diffDays < 7) {
        counts[6 - diffDays]++;
      }
    });
    const labels = Array.from({ length: 7 }, (_, i) => {
      const d = new Date(now);
      d.setDate(d.getDate() - (6 - i));
      return days[d.getDay()];
    });
    new Chart(trends, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: 'Migrations',
          data: counts,
          borderColor: '#8B7CFF',
          backgroundColor: 'rgba(139,124,255,0.14)',
          tension: 0.35,
          fill: true,
        }],
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { display: false }, ticks: { color: '#9CA3AF' } },
          y: { grid: { color: 'rgba(255,255,255,0.08)' }, ticks: { color: '#9CA3AF' } },
        },
      },
    });
  }

  // --- Activity bar: users / migrations / reports ---
  const activity = document.getElementById('user-activity-chart');
  if (activity) {
    const totalUsers = adminStats.total_users || adminStats.totalUsers || '—';
    const totalMigrations = history.length;
    const totalReports = history.filter((r) => r.report_summary).length;
    new Chart(activity, {
      type: 'bar',
      data: {
        labels: ['Users', 'Migrations', 'Reports'],
        datasets: [{
          label: 'Total',
          data: [totalUsers, totalMigrations, totalReports],
          backgroundColor: ['#6366F1', '#22C55E', '#F59E0B'],
        }],
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          x: { ticks: { color: '#9CA3AF' } },
          y: { grid: { color: 'rgba(255,255,255,0.08)' }, ticks: { color: '#9CA3AF' } },
        },
      },
    });
  }

  // --- DB usage doughnut: derived from migration source_db field ---
  const usage = document.getElementById('database-usage-chart');
  if (usage) {
    const dbCounts = { MySQL: 0, PostgreSQL: 0, Oracle: 0, SQLite: 0, Other: 0 };
    history.forEach((r) => {
      const src = (r.source_db || '').toLowerCase();
      if (src.includes('mysql')) dbCounts.MySQL++;
      else if (src.includes('postgres')) dbCounts.PostgreSQL++;
      else if (src.includes('oracle')) dbCounts.Oracle++;
      else if (src.includes('sqlite') || src.endsWith('.db')) dbCounts.SQLite++;
      else dbCounts.Other++;
    });
    const labels = Object.keys(dbCounts).filter((k) => dbCounts[k] > 0);
    const data = labels.map((k) => dbCounts[k]);
    new Chart(usage, {
      type: 'doughnut',
      data: {
        labels,
        datasets: [{
          data,
          backgroundColor: ['#8B7CFF', '#22C55E', '#F59E0B', '#EF4444', '#60A5FA'],
        }],
      },
      options: {
        responsive: true,
        plugins: { legend: { position: 'bottom', labels: { color: '#9CA3AF' } } },
      },
    });
  }
}
