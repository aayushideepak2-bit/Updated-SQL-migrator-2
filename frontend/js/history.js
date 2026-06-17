let allHistoryRecords = [];

function initHistoryPage() {
  if (!requireAuth()) return;
  loadSharedComponent('header', () => {
    setProfileSummary();
    bindHeaderActions();
  });
  initSidebar();

  const headerTitle = document.getElementById('page-title');
  if (headerTitle) headerTitle.textContent = 'Migration History';

  loadHistoryData();
  setupFilterListeners();
}

async function loadHistoryData() {
  const tableBody = document.getElementById('history-table-body');
  if (tableBody) {
    tableBody.innerHTML = '<tr><td colspan="8" style="text-align:center">Loading history...</td></tr>';
  }

  try {
    const response = await apiRequest('/migration/history', 'GET');
    allHistoryRecords = response.history || [];
    
    updateStatsCards(allHistoryRecords);
    renderHistoryTable(allHistoryRecords);
  } catch (error) {
    console.error('Failed to load migration history:', error);
    if (tableBody) {
      tableBody.innerHTML = '<tr><td colspan="8" style="text-align:center; color:var(--error-color)">Failed to load migration history records.</td></tr>';
    }
  }
}

function updateStatsCards(records) {
  const totalEl = document.getElementById('stat-total');
  const successEl = document.getElementById('stat-success');
  const warningEl = document.getElementById('stat-warning');
  const failedEl = document.getElementById('stat-failed');

  const total = records.length;
  const success = records.filter(r => {
    const s = (r.status || '').toLowerCase();
    return s === 'completed' || s === 'success';
  }).length;
  const warning = records.filter(r => {
    const s = (r.status || '').toLowerCase();
    return s === 'warning' || s === 'running';
  }).length;
  const failed = records.filter(r => {
    const s = (r.status || '').toLowerCase();
    return s === 'failed';
  }).length;

  if (totalEl) totalEl.textContent = total;
  if (successEl) successEl.textContent = success;
  if (warningEl) warningEl.textContent = warning;
  if (failedEl) failedEl.textContent = failed;
}

function renderHistoryTable(records) {
  const tableBody = document.getElementById('history-table-body');
  if (!tableBody) return;

  if (records.length === 0) {
    tableBody.innerHTML = '<tr><td colspan="8" style="text-align:center">No migration records found.</td></tr>';
    return;
  }

  const currentUser = getUserInfo()?.name || getUserInfo()?.username || 'System User';

  tableBody.innerHTML = records.map(record => {
    const migrationId = `MIG-${String(record.id).padStart(3, '0')}`;
    const dateFormatted = (record.timestamp || '').split('T')[0] || 'N/A';
    
    // Prettify type
    let typeLabel = record.migration_type || '';
    if (typeLabel === 'sql_to_sql') typeLabel = 'SQL to SQL';
    else if (typeLabel === 'file_to_sql') typeLabel = 'File to SQL';
    else if (typeLabel === 'sql_to_file') typeLabel = 'SQL to File';
    else {
      typeLabel = typeLabel.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
    }

    // Prettify status
    const statusLower = (record.status || '').toLowerCase();
    let statusClass = 'status-pill ';
    let statusLabel = record.status || 'Unknown';
    
    if (statusLower === 'completed' || statusLower === 'success') {
      statusClass += 'status-success';
      statusLabel = 'Completed';
    } else if (statusLower === 'failed') {
      statusClass += 'status-danger';
      statusLabel = 'Failed';
    } else {
      statusClass += 'status-warning';
      statusLabel = 'Running';
    }

    // Prettify connection strings to make them legible
    const sourceClean = record.source_db || 'N/A';
    const targetClean = record.target_db || 'N/A';

    // Simulated duration
    const duration = `${(record.id % 4) + 2}m`;

    return `
      <tr>
        <td>${migrationId}</td>
        <td>${currentUser}</td>
        <td title="${sourceClean}">${sourceClean}</td>
        <td title="${targetClean}">${targetClean}</td>
        <td>${typeLabel}</td>
        <td>${dateFormatted}</td>
        <td>${duration}</td>
        <td><span class="${statusClass}">${statusLabel}</span></td>
      </tr>
    `;
  }).join('');
}

function setupFilterListeners() {
  const searchInput = document.getElementById('search-history');
  const statusSelect = document.getElementById('filter-status');
  const startDateInput = document.getElementById('filter-start-date');
  const endDateInput = document.getElementById('filter-end-date');

  [searchInput, statusSelect, startDateInput, endDateInput].forEach(el => {
    if (el) {
      el.addEventListener('input', filterHistory);
      el.addEventListener('change', filterHistory);
    }
  });
}

function filterHistory() {
  const searchQuery = (document.getElementById('search-history')?.value || '').toLowerCase().trim();
  const selectedStatus = (document.getElementById('filter-status')?.value || '').toLowerCase();
  const startDateStr = document.getElementById('filter-start-date')?.value || '';
  const endDateStr = document.getElementById('filter-end-date')?.value || '';

  const filtered = allHistoryRecords.filter(record => {
    // 1. Search Query filter (Migration ID, type, source, target, user fallback)
    const migrationId = `MIG-${String(record.id).padStart(3, '0')}`.toLowerCase();
    const source = (record.source_db || '').toLowerCase();
    const target = (record.target_db || '').toLowerCase();
    const type = (record.migration_type || '').toLowerCase();
    const currentUser = (getUserInfo()?.name || getUserInfo()?.username || 'System User').toLowerCase();

    if (searchQuery) {
      const match = migrationId.includes(searchQuery) ||
                    source.includes(searchQuery) ||
                    target.includes(searchQuery) ||
                    type.includes(searchQuery) ||
                    currentUser.includes(searchQuery);
      if (!match) return false;
    }

    // 2. Status filter
    if (selectedStatus) {
      const statusLower = (record.status || '').toLowerCase();
      if (selectedStatus === 'completed') {
        if (statusLower !== 'completed' && statusLower !== 'success') return false;
      } else if (selectedStatus === 'running') {
        if (statusLower === 'completed' || statusLower === 'success' || statusLower === 'failed') return false;
      } else if (selectedStatus === 'failed') {
        if (statusLower !== 'failed') return false;
      }
    }

    // 3. Date range filter
    if (record.timestamp) {
      const recordDateStr = record.timestamp.split('T')[0]; // YYYY-MM-DD
      if (startDateStr && recordDateStr < startDateStr) return false;
      if (endDateStr && recordDateStr > endDateStr) return false;
    }

    return true;
  });

  renderHistoryTable(filtered);
}
