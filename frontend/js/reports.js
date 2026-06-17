const _historyCache = {};

function initReportsPage() {
  if (!requireAuth()) return;
  loadSharedComponent('header', () => {
    setProfileSummary();
    bindHeaderActions();
  });
  initSidebar();
  const headerTitle = document.getElementById('page-title');
  if (headerTitle) headerTitle.textContent = 'Reports';
  injectReportModal();
  renderReportSummary();
  renderReportTable();
}

async function renderReportTable() {
  const response = await apiRequest('/history', 'GET');
  const history = response.history || [];
  const tableBody = document.getElementById('reports-table-body');
  if (!tableBody) return;

  if (history.length === 0) {
    tableBody.innerHTML = '<tr><td colspan="6">No reports found.</td></tr>';
    return;
  }

  history.forEach((r) => { _historyCache[r.id] = r; });

  tableBody.innerHTML = history.map((record) => {
    const statusClass = record.status === 'completed' ? 'status-success' : 'status-danger';
    const date = record.timestamp ? new Date(record.timestamp).toLocaleString() : '—';
    return `
      <tr>
        <td>#${record.id}</td>
        <td>${record.migration_type || '—'}</td>
        <td>${record.source_db || '—'}</td>
        <td>${date}</td>
        <td><span class="status-pill ${statusClass}">${record.status}</span></td>
        <td>
          <button class="button-secondary" onclick="viewReport(${record.id})">View</button>
        </td>
      </tr>
    `;
  }).join('');
}

function viewReport(recordId) {
  const record = _historyCache[recordId];
  if (!record) return;

  let summary = [];
  try {
    const parsed = JSON.parse(record.report_summary || 'null');
    if (Array.isArray(parsed)) summary = parsed;
    else if (parsed && typeof parsed === 'object') summary = [parsed];
  } catch (_) {}

  const date = record.timestamp ? new Date(record.timestamp).toLocaleString() : '—';

  let summaryHTML = '';
  if (summary.length > 0) {
    summaryHTML = summary.map((row) => {
      const ok = row.status === 'completed';
      const skipped = row.status === 'skipped';
      const icon = ok ? '✅' : skipped ? '⏭️' : '❌';
      const statusClass = ok ? 'status-success' : skipped ? 'status-warning' : 'status-danger';
      const name = row.table || row.table_name || row.file_name || '—';
      const rows = row.rows_transferred != null
        ? `${Number(row.rows_transferred).toLocaleString()} rows transferred`
        : row.rows_imported != null
          ? `${Number(row.rows_imported).toLocaleString()} rows imported`
          : '';
      const validation = row.validation
        ? `Source: ${row.validation.source_count ?? '—'} | Target: ${row.validation.target_count ?? '—'}`
        : '';
      const detail = [rows, validation].filter(Boolean).join(' &nbsp;·&nbsp; ');
      const errorHTML = row.error
        ? `<p class="msr-error">⚠️ ${row.error}</p>` : '';
      const reasonHTML = row.reason
        ? `<p class="msr-detail">${row.reason}</p>` : '';
      return `
        <div class="migration-summary-row">
          <span class="msr-icon">${icon}</span>
          <div class="msr-body">
            <span class="msr-name">${name}</span>
            ${detail ? `<p class="msr-detail">${detail}</p>` : ''}
            ${errorHTML}${reasonHTML}
          </div>
          <span class="status-pill ${statusClass} msr-status">${row.status}</span>
        </div>`;
    }).join('');
  } else if (record.errors) {
    summaryHTML = `
      <div class="migration-summary-row">
        <span class="msr-icon">❌</span>
        <div class="msr-body">
          <span class="msr-name">Migration failed</span>
          <p class="msr-error">${record.errors}</p>
        </div>
      </div>`;
  } else {
    summaryHTML = '<p style="color:var(--muted);font-size:0.9rem;">No details available.</p>';
  }

  document.getElementById('modal-title').textContent = `Report #${record.id}`;
  document.getElementById('modal-type').textContent = record.migration_type || '—';
  document.getElementById('modal-source').textContent = record.source_db || '—';
  document.getElementById('modal-target').textContent = record.target_db || '—';
  document.getElementById('modal-date').textContent = date;

  const statusEl = document.getElementById('modal-status');
  statusEl.textContent = record.status;
  statusEl.className = `status-pill ${record.status === 'completed' ? 'status-success' : 'status-danger'}`;

  document.getElementById('modal-summary-rows').innerHTML = summaryHTML;
  document.getElementById('report-modal').classList.add('modal-open');
  document.body.classList.add('modal-active');
}

function closeReportModal() {
  document.getElementById('report-modal').classList.remove('modal-open');
  document.body.classList.remove('modal-active');
}

function injectReportModal() {
  if (document.getElementById('report-modal')) return;
  const modal = document.createElement('div');
  modal.id = 'report-modal';
  modal.className = 'modal-overlay';
  modal.innerHTML = `
    <div class="modal-box">
      <div class="modal-header">
        <h2 id="modal-title">Report</h2>
        <button class="button-secondary modal-close" onclick="closeReportModal()">✕ Close</button>
      </div>
      <div class="modal-meta">
        <div class="modal-meta-row">
          <span class="modal-label">Type</span>
          <span class="modal-value" id="modal-type">—</span>
        </div>
        <div class="modal-meta-row">
          <span class="modal-label">Status</span>
          <span id="modal-status" class="status-pill">—</span>
        </div>
        <div class="modal-meta-row">
          <span class="modal-label">Source</span>
          <span class="modal-value" id="modal-source">—</span>
        </div>
        <div class="modal-meta-row">
          <span class="modal-label">Target</span>
          <span class="modal-value" id="modal-target">—</span>
        </div>
        <div class="modal-meta-row">
          <span class="modal-label">Generated</span>
          <span class="modal-value" id="modal-date">—</span>
        </div>
      </div>
      <div>
        <p class="modal-section-title">Migration Summary</p>
        <div id="modal-summary-rows"></div>
      </div>
      <div class="modal-footer">
        <button class="button-secondary" onclick="closeReportModal()">Close</button>
      </div>
    </div>
  `;
  modal.addEventListener('click', (e) => {
    if (e.target === modal) closeReportModal();
  });
  document.body.appendChild(modal);
}

async function renderReportSummary() {
  const response = await apiRequest('/history', 'GET');
  const history = response.history || [];
  const total = history.length;
  const today = history.filter((r) => {
    if (!r.timestamp) return false;
    return new Date(r.timestamp).toDateString() === new Date().toDateString();
  }).length;
  const sqlMigrations = history.filter((r) => r.migration_type === 'sql_to_sql').length;
  const fileImports = history.filter((r) => r.migration_type !== 'sql_to_sql').length;

  const container = document.getElementById('report-summary');
  if (!container) return;
  container.innerHTML = `
    <div class="card metric-card"><h3>Total Reports</h3><strong>${total}</strong></div>
    <div class="card metric-card"><h3>Generated Today</h3><strong>${today}</strong></div>
    <div class="card metric-card"><h3>SQL Migrations</h3><strong>${sqlMigrations}</strong></div>
    <div class="card metric-card"><h3>File Imports</h3><strong>${fileImports}</strong></div>
  `;
}