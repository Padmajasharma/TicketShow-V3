<template>
  <div class="admin-analytics page container">
    <div class="page-header">
      <div class="breadcrumbs">Admin / Analytics</div>
      <div class="title-row">
        <div>
          <h1 class="page-title">Sales Analytics</h1>
          <div class="subtitle">Bookings, revenue and trends — filter, export or inspect.</div>
        </div>
        <div class="top-actions">
          <button class="btn btn-action" @click="goBack" title="Back">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <polyline points="15 18 9 12 15 6"></polyline>
            </svg>
            Back
          </button>
          <button class="btn btn-action" @click="goToDashboard" title="Dashboard">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
            </svg>
            Dashboard
          </button>
          <button class="btn btn-danger" @click="logout" title="Logout">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
              <polyline points="16 17 21 12 16 7"></polyline>
              <line x1="21" y1="12" x2="9" y2="12"></line>
            </svg>
            Logout
          </button>
        </div>
      </div>
      <div class="header-actions">
        <div class="last-fetched">Last: <strong>{{ lastFetchedLabel }}</strong></div>
        <button class="btn btn-refresh" @click="fetchData" title="Refresh">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <polyline points="23 4 23 10 17 10"></polyline>
            <polyline points="1 20 1 14 7 14"></polyline>
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
          </svg>
          Refresh
        </button>
      </div>
    </div>

    <div class="controls-card">
      <div class="controls-row">
        <div class="control-group">
          <label class="control-label">Group by</label>
          <select v-model="groupBy" class="control-select">
            <option value="movie">Movies</option>
            <option value="concert">Concerts</option>
            <option value="play">Plays</option>
            <option value="event">Events</option>
            <option value="theatre">Theatres</option>
            <option value="city">City</option>
          </select>
        </div>

        <div class="date-controls">
          <div class="control-group">
            <label class="control-label">Start Date</label>
            <input type="date" v-model="start" class="control-input" />
          </div>
          <div class="control-group">
            <label class="control-label">End Date</label>
            <input type="date" v-model="end" class="control-input" />
          </div>
        </div>

        <div class="toggles-group">
          <label class="toggle-label">
            <input type="checkbox" v-model="allTime" class="toggle-checkbox" />
            <span class="toggle-text">All time</span>
          </label>
          <label class="toggle-label">
            <input type="checkbox" v-model="includeUnconfirmed" class="toggle-checkbox" />
            <span class="toggle-text">Include unconfirmed</span>
          </label>
          <label class="toggle-label">
            <input type="checkbox" v-model="showZeros" class="toggle-checkbox" />
            <span class="toggle-text">Show zeros</span>
          </label>
        </div>
      </div>

      <div class="controls-actions">
        <button class="btn btn-secondary" @click="resetRange">Reset</button>
        <button class="btn btn-primary" @click="fetchData">Fetch Data</button>
        <button class="btn btn-secondary" @click="exportCsv">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="7 10 12 15 17 10"></polyline>
            <line x1="12" y1="15" x2="12" y2="3"></line>
          </svg>
          Export CSV
        </button>
      </div>
    </div>

    <div class="content-area">
      <div v-if="loading" class="loading-card">
        <div class="loading-spinner"></div>
        <p>Loading analytics...</p>
      </div>

      <div v-if="error" class="error-card">
        <svg class="error-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="12"></line>
          <line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
        <p>{{ error }}</p>
      </div>

      <div v-if="data.length > 0" class="results-container">
        <div class="summary-cards">
          <div class="summary-card">
            <div class="summary-icon bookings-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
              </svg>
            </div>
            <div class="summary-content">
              <div class="summary-label">Total Bookings</div>
              <div class="summary-value">{{ totalBookings.toLocaleString() }}</div>
            </div>
          </div>

          <div class="summary-card">
            <div class="summary-icon revenue-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <line x1="12" y1="1" x2="12" y2="23"></line>
                <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
              </svg>
            </div>
            <div class="summary-content">
              <div class="summary-label">Total Revenue</div>
              <div class="summary-value">₹{{ formatRevenue(totalRevenue) }}</div>
            </div>
          </div>

          <div class="summary-card">
            <div class="summary-icon group-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                <polyline points="9 22 9 12 15 12 15 22"></polyline>
              </svg>
            </div>
            <div class="summary-content">
              <div class="summary-label">Grouped By</div>
              <div class="summary-group">{{ groupLabel }}</div>
              <div class="summary-meta">{{ filteredData.length }} rows</div>
            </div>
          </div>
        </div>

        <div class="chart-card">
          <h3 class="chart-title">Top Performers by Revenue</h3>
          <div v-if="topShows.length === 0" class="chart-empty">No data to display</div>
          <svg v-else :width="chartWidth" :height="chartHeight" class="revenue-chart">
            <g v-for="(s, idx) in topShows" :key="(s.show_id || s.city) + '-' + idx" :transform="`translate(0, ${idx * barStep})`">
              <rect :x="160" :y="6" :width="barWidth(s.revenue)" :height="barHeight" class="bar-fill" rx="8" />
              <text x="8" :y="barHeight + 4" font-size="13" fill="#2d3748" class="bar-label">{{ truncate((s.name || s.city) || '—', 18) }}</text>
              <text :x="160 + barWidth(s.revenue) + 12" :y="barHeight + 4" font-size="12" fill="#718096" class="bar-value">₹{{ formatRevenue(s.revenue) }}</text>
            </g>
          </svg>
        </div>

        <div class="table-card">
          <div class="table-header">
            <h3 class="table-title">Detailed Results</h3>
          </div>

          <div class="table-wrapper">
            <table class="data-table">
              <thead>
                <tr>
                  <th v-if="isShowResult" @click="sortBy('show_id')" class="sortable">
                    Show ID
                    <span v-if="sortKey==='show_id'" class="sort-icon">{{ sortDesc ? '↓' : '↑' }}</span>
                  </th>
                  <th v-if="isShowResult" @click="sortBy('name')" class="sortable">
                    Name
                    <span v-if="sortKey==='name'" class="sort-icon">{{ sortDesc ? '↓' : '↑' }}</span>
                  </th>
                  <th v-if="isCityResult">City</th>
                  <th @click="sortBy('bookings')" class="sortable">
                    Bookings
                    <span v-if="sortKey==='bookings'" class="sort-icon">{{ sortDesc ? '↓' : '↑' }}</span>
                  </th>
                  <th @click="sortBy('revenue')" class="sortable">
                    Revenue
                    <span v-if="sortKey==='revenue'" class="sort-icon">{{ sortDesc ? '↓' : '↑' }}</span>
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in paginatedData" :key="(row.show_id || row.city) + '-' + (row.bookings || 0)">
                  <td v-if="isShowResult">{{ row.show_id ?? '-' }}</td>
                  <td v-if="isShowResult" class="name-cell">{{ row.name ?? '-' }}</td>
                  <td v-if="isCityResult">{{ row.city ?? '-' }}</td>
                  <td>{{ (row.bookings ?? 0).toLocaleString() }}</td>
                  <td class="revenue-cell">₹{{ formatRevenue(row.revenue) }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="pagination">
            <div class="pagination-info">
              <span class="pagination-label">Rows per page:</span>
              <select v-model.number="pageSize" class="pagination-select">
                <option v-for="s in pageSizes" :key="s" :value="s">{{ s }}</option>
              </select>
            </div>
            <div class="pagination-controls">
              <button class="pagination-btn" :disabled="page<=1" @click="changePage(page-1)">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <polyline points="15 18 9 12 15 6"></polyline>
                </svg>
              </button>
              <span class="pagination-text">Page {{ page }} of {{ totalPages }}</span>
              <button class="pagination-btn" :disabled="page>=totalPages" @click="changePage(page+1)">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <polyline points="9 18 15 12 9 6"></polyline>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="!loading" class="empty-card">
        <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path>
        </svg>
        <p class="empty-text">No data available for the selected period</p>
        <p class="empty-subtext">Try adjusting your date range or filters</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'AdminAnalytics',
  data() {
    return {
      groupBy: 'movie',
      start: '',
      end: '',
      allTime: true,
      includeUnconfirmed: true,
      showZeros: false,
      lastFetched: null,
      sortKey: 'revenue',
      sortDesc: true,
      page: 1,
      pageSize: 10,
      pageSizes: [5, 10, 20, 50],
      data: [],
      loading: false,
      error: ''
    };
  },
  methods: {
    async fetchData() {
      this.loading = true;
      this.error = '';
      this.data = [];
      try {
        const params = {};
        if (this.groupBy) params.group_by = this.groupBy;
        if (this.allTime) {
          params.since_days = 0;
        } else {
          if (this.start) params.start = this.start;
          if (this.end) params.end = this.end;
        }
        if (this.includeUnconfirmed) params.include_unconfirmed = 1;
        const resp = await axios.get('/analytics/sales', { params });
        this.data = Array.isArray(resp.data?.data) ? resp.data.data : [];
        this.lastFetched = new Date();
      } catch (err) {
        console.error('Analytics fetch error', err);
        this.error = err.response?.data?.message || err.message || 'Failed to fetch analytics';
      } finally {
        this.loading = false;
      }
    },
    formatRevenue(v) {
      try {
        const n = Number(v || 0);
        return new Intl.NumberFormat('en-IN', { 
          style: 'currency', 
          currency: 'INR', 
          maximumFractionDigits: 2 
        }).format(n).replace('₹', '').trim();
      } catch (e) {
        return '0.00';
      }
    },
    truncate(str, len) {
      if (!str || str.length <= len) return str;
      return str.substring(0, len) + '...';
    },
    resetRange() {
      const today = new Date();
      const prior = new Date();
      prior.setDate(today.getDate() - 30);
      this.end = today.toISOString().slice(0,10);
      this.start = prior.toISOString().slice(0,10);
      this.allTime = false;
      this.fetchData();
    },
    sortBy(key) {
      if (this.sortKey === key) {
        this.sortDesc = !this.sortDesc;
      } else {
        this.sortKey = key;
        this.sortDesc = true;
      }
      this.page = 1;
    },
    changePage(n) {
      if (n < 1) n = 1;
      if (n > this.totalPages) n = this.totalPages;
      this.page = n;
    },
    barWidth(val) {
      const v = Number(val || 0);
      if (this.maxRevenue <= 0) return 0;
      const maxW = Math.max(200, Math.min(500, this.chartWidth - 200));
      return Math.round((v / this.maxRevenue) * maxW);
    },
    goBack() {
      try {
        this.$router.back();
      } catch (e) {
        window.history.back();
      }
    },
    goToDashboard() {
      const isAdmin = localStorage.getItem('is_admin') === 'true';
      if (isAdmin) {
        this.$router.push('/admindashboard');
      } else {
        this.$router.push('/userdashboard');
      }
    },
    logout() {
      try {
        localStorage.removeItem('access_token');
        localStorage.removeItem('is_admin');
      } catch (e) {
        console.error('Logout error:', e);
      }
      this.$router.push('/login');
    },
    exportCsv() {
      const rows = this.sortedData;
      if (!rows || rows.length === 0) {
        alert('No data to export');
        return;
      }

      const escape = (v) => {
        if (v == null) return '';
        const s = String(v);
        if (/[",\n\r]/.test(s)) return '"' + s.replace(/"/g, '""') + '"';
        return s;
      };

      const cols = this.groupBy === 'city' ? ['city', 'bookings', 'revenue'] : ['show_id', 'name', 'bookings', 'revenue'];
      const header = cols.map(c => c.toUpperCase()).join(',');
      const dataLines = rows.map(r => {
        if (this.groupBy === 'city') {
          return [escape(r.city), escape(r.bookings), escape(r.revenue)].join(',');
        }
        return [escape(r.show_id), escape(r.name), escape(r.bookings), escape(r.revenue)].join(',');
      });

      const csv = [header].concat(dataLines).join('\r\n');

      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const ts = new Date().toISOString().slice(0,19).replace(/[:T]/g, '-');
      const filename = `analytics_${this.groupBy}_${ts}.csv`;
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    },
  },
  computed: {
    isShowResult() {
      return this.data && this.data.length > 0 && (this.data[0].hasOwnProperty('show_id') || this.data[0].hasOwnProperty('name'));
    },
    isCityResult() {
      return this.data && this.data.length > 0 && this.data[0].hasOwnProperty('city');
    },
    groupLabel() {
      const map = { movie: 'Movies', concert: 'Concerts', play: 'Plays', event: 'Events', theatre: 'Theatres', city: 'City' };
      return map[this.groupBy] || this.groupBy;
    },
    lastFetchedLabel() {
      if (!this.lastFetched) return 'never';
      try {
        return new Date(this.lastFetched).toLocaleString();
      } catch (e) {
        return this.lastFetched;
      }
    },
    totalBookings() {
      return this.filteredData.reduce((s, r) => s + (Number(r.bookings) || 0), 0);
    },
    totalRevenue() {
      return this.filteredData.reduce((s, r) => s + (Number(r.revenue) || 0), 0);
    },
    filteredData() {
      if (this.showZeros) return this.data;
      return this.data.filter(r => Number(r.bookings || 0) > 0);
    },
    sortedData() {
      const key = this.sortKey;
      const desc = this.sortDesc ? -1 : 1;
      return [...this.filteredData].sort((a, b) => {
        const va = a[key] == null ? 0 : a[key];
        const vb = b[key] == null ? 0 : b[key];
        if (typeof va === 'string') return desc * va.localeCompare(vb);
        return desc * (Number(va) - Number(vb));
      });
    },
    totalPages() {
      return Math.max(1, Math.ceil(this.sortedData.length / this.pageSize));
    },
    paginatedData() {
      const start = (this.page - 1) * this.pageSize;
      return this.sortedData.slice(start, start + this.pageSize);
    },
    topShows() {
      return this.sortedData.slice(0, 6);
    },
    maxRevenue() {
      return Math.max(0, ...this.data.map(d => Number(d.revenue || 0)));
    },
    chartWidth() { return 800; },
    chartHeight() { return Math.max(140, this.topShows.length * 32); },
    barStep() { return 32; },
    barHeight() { return 20; },
  },
  mounted() {
    const today = new Date();
    const prior = new Date();
    prior.setDate(today.getDate() - 30);
    this.end = today.toISOString().slice(0,10);
    this.start = prior.toISOString().slice(0,10);
    this.fetchData();
  }
};
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.admin-analytics {
  min-height: 100vh;
  background: linear-gradient(135deg, #fdf4f5 0%, #f7e7f0 50%, #e8f4f8 100%);
  padding: 32px 20px;
  max-width: 1400px;
  margin: 0 auto;
}

/* Page Header */
.page-header {
  margin-bottom: 32px;
}

.breadcrumbs {
  font-size: 13px;
  color: #a0aec0;
  margin-bottom: 12px;
  font-weight: 500;
}

.title-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 24px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  color: #2d3748;
  margin: 0 0 8px 0;
  letter-spacing: -0.5px;
}

.subtitle {
  font-size: 15px;
  color: #718096;
  margin: 0;
}

.top-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.btn-action {
  background: rgba(255, 255, 255, 0.8);
  color: #2d3748;
  border: 2px solid #f0e7ef;
  padding: 10px 18px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-action:hover {
  background: #ffffff;
  border-color: #d4a5c5;
  transform: translateY(-2px);
}

.btn-danger {
  background: linear-gradient(135deg, #fed7d7, #fc8181);
  color: #ffffff;
  border: none;
  padding: 10px 18px;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 4px 12px rgba(252, 129, 129, 0.3);
}

.btn-danger:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(252, 129, 129, 0.4);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.last-fetched {
  font-size: 13px;
  color: #718096;
  padding: 10px 16px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 12px;
  border: 1px solid rgba(240, 231, 239, 0.5);
}

.last-fetched strong {
  color: #2d3748;
}

.btn-refresh {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: linear-gradient(135deg, #e8c4d8, #d4a5c5);
  color: #ffffff;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(212, 165, 197, 0.3);
}

.btn-refresh svg {
  width: 16px;
  height: 16px;
  stroke-width: 2;
}

.btn-refresh:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(212, 165, 197, 0.4);
}

/* Controls Card */
.controls-card {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 8px 24px rgba(212, 165, 197, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.8);
}

.controls-row {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 160px;
}

.control-label {
  font-size: 13px;
  color: #718096;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.control-select,
.control-input {
  padding: 12px 16px;
  border: 2px solid #f0e7ef;
  border-radius: 12px;
  font-size: 14px;
  color: #2d3748;
  background: #fafafa;
  transition: all 0.3s ease;
  font-family: inherit;
}

.control-select:focus,
.control-input:focus {
  outline: none;
  border-color: #d4a5c5;
  background: #ffffff;
}

.date-controls {
  display: flex;
  gap: 16px;
}

.toggles-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
  justify-content: center;
}

.toggle-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.toggle-checkbox {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: #d4a5c5;
}

.toggle-text {
  font-size: 14px;
  color: #2d3748;
}

.controls-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.btn {
  padding: 12px 24px;
  border-radius: 12px;
  border: none;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: inherit;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn svg {
  width: 16px;
  height: 16px;
  stroke-width: 2;
}

.btn-primary {
  background: linear-gradient(135deg, #e8c4d8, #d4a5c5);
  color: #ffffff;
  box-shadow: 0 4px 12px rgba(212, 165, 197, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(212, 165, 197, 0.4);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.8);
  color: #2d3748;
  border: 2px solid #f0e7ef;
}

.btn-secondary:hover {
  background: #ffffff;
  border-color: #d4a5c5;
  transform: translateY(-2px);
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* Content Area */
.content-area {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Loading */
.loading-card {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 64px 32px;
  text-align: center;
  box-shadow: 0 8px 24px rgba(212, 165, 197, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.8);
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #f0e7ef;
  border-top-color: #d4a5c5;
  border-radius: 50%;
  margin: 0 auto 16px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-card p {
  color: #718096;
  font-size: 15px;
  margin: 0;
}

/* Error */
.error-card {
  background: rgba(254, 215, 215, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 8px 24px rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(248, 113, 113, 0.3);
}

.error-icon {
  width: 24px;
  height: 24px;
  stroke: #c53030;
  stroke-width: 2;
  flex-shrink: 0;
}

.error-card p {
  color: #c53030;
  margin: 0;
  font-size: 14px;
}

/* Empty State */
.empty-card {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 64px 32px;
  text-align: center;
  box-shadow: 0 8px 24px rgba(212, 165, 197, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.8);
}

.empty-icon {
  width: 64px;
  height: 64px;
  stroke: #d4a5c5;
  stroke-width: 1.5;
  margin: 0 auto 20px;
  opacity: 0.6;
}

.empty-text {
  font-size: 16px;
  color: #2d3748;
  font-weight: 600;
  margin: 0 0 8px 0;
}

.empty-subtext {
  font-size: 14px;
  color: #a0aec0;
  margin: 0;
}

/* Results Container */
.results-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Summary Cards */
.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.summary-card {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 8px 24px rgba(212, 165, 197, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.8);
  display: flex;
  gap: 20px;
  align-items: flex-start;
  transition: transform 0.3s ease;
}

.summary-card:hover {
  transform: translateY(-4px);
}

.summary-icon {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.summary-icon svg {
  width: 24px;
  height: 24px;
  stroke-width: 2;
}

.bookings-icon {
  background: linear-gradient(135deg, #e8c4d8, #d4a5c5);
}

.bookings-icon svg {
  stroke: #ffffff;
}

.revenue-icon {
  background: linear-gradient(135deg, #c8e6c9, #a5d6a7);
}

.revenue-icon svg {
  stroke: #ffffff;
}

.group-icon {
  background: linear-gradient(135deg, #c5cae9, #9fa8da);
}

.group-icon svg {
  stroke: #ffffff;
}

.summary-content {
  flex: 1;
}

.summary-label {
  font-size: 13px;
  color: #718096;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  font-weight: 500;
  margin-bottom: 8px;
}

.summary-value {
  font-size: 28px;
  font-weight: 700;
  color: #2d3748;
  letter-spacing: -0.5px;
}

.summary-group {
  font-size: 20px;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 4px;
}

.summary-meta {
  font-size: 13px;
  color: #a0aec0;
}

/* Chart Card */
.chart-card {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 28px;
  box-shadow: 0 8px 24px rgba(212, 165, 197, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.8);
}

.chart-title {
  font-size: 18px;
  font-weight: 600;
  color: #2d3748;
  margin: 0 0 24px 0;
}

.chart-empty {
  text-align: center;
  color: #a0aec0;
  padding: 40px;
  font-size: 14px;
}

.revenue-chart {
  width: 100%;
  max-width: 100%;
  height: auto;
}

.revenue-chart .bar-fill {
  fill: #d4a5c5;
}

.bar-label {
  font-weight: 500;
}

.bar-value {
  font-weight: 600;
}

/* Table Card */
.table-card {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 28px;
  box-shadow: 0 8px 24px rgba(212, 165, 197, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.8);
}

.table-header {
  margin-bottom: 20px;
}

.table-title {
  font-size: 18px;
  font-weight: 600;
  color: #2d3748;
  margin: 0;
}

.table-wrapper {
  overflow-x: auto;
  border-radius: 12px;
  margin-bottom: 20px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table thead {
  background: linear-gradient(135deg, #f8f4f7, #f5f0f4);
}

.data-table th {
  padding: 14px 16px;
  text-align: left;
  font-size: 13px;
  font-weight: 600;
  color: #2d3748;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  border-bottom: 2px solid #f0e7ef;
}

.data-table th.sortable {
  cursor: pointer;
  user-select: none;
  transition: background-color 0.3s ease;
}

.data-table th.sortable:hover {
  background-color: rgba(212, 165, 197, 0.1);
}

.sort-icon {
  display: inline-block;
  margin-left: 4px;
  color: #d4a5c5;
  font-weight: bold;
}

.data-table tbody tr {
  border-bottom: 1px solid rgba(240, 231, 239, 0.5);
  transition: background-color 0.3s ease;
}

.data-table tbody tr:hover {
  background-color: rgba(212, 165, 197, 0.08);
}

.data-table td {
  padding: 14px 16px;
  font-size: 14px;
  color: #2d3748;
}

.name-cell {
  font-weight: 500;
}

.revenue-cell {
  font-weight: 600;
  color: #d4a5c5;
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 20px;
  border-top: 1px solid rgba(240, 231, 239, 0.5);
  flex-wrap: wrap;
  gap: 16px;
}

.pagination-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.pagination-label {
  font-size: 14px;
  color: #718096;
}

.pagination-select {
  padding: 8px 12px;
  border: 2px solid #f0e7ef;
  border-radius: 8px;
  font-size: 14px;
  color: #2d3748;
  background: #fafafa;
  cursor: pointer;
  transition: all 0.3s ease;
}

.pagination-select:focus {
  outline: none;
  border-color: #d4a5c5;
  background: #ffffff;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.pagination-btn {
  width: 36px;
  height: 36px;
  border: 2px solid #f0e7ef;
  border-radius: 8px;
  background: #ffffff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.pagination-btn svg {
  width: 20px;
  height: 20px;
  stroke: #2d3748;
  stroke-width: 2;
}

.pagination-btn:hover:not(:disabled) {
  border-color: #d4a5c5;
  background: rgba(212, 165, 197, 0.1);
  transform: translateY(-2px);
}

.pagination-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.pagination-text {
  font-size: 14px;
  color: #2d3748;
  font-weight: 500;
}

/* Responsive */
@media (max-width: 768px) {
  .title-row {
    flex-direction: column;
  }

  .top-actions {
    width: 100%;
  }

  .btn-action,
  .btn-danger {
    flex: 1;
    justify-content: center;
  }

  .header-actions {
    flex-direction: column;
    width: 100%;
  }

  .last-fetched {
    width: 100%;
    text-align: center;
  }

  .btn-refresh {
    width: 100%;
    justify-content: center;
  }

  .controls-row {
    flex-direction: column;
  }

  .date-controls {
    flex-direction: column;
    width: 100%;
  }

  .control-group {
    width: 100%;
  }

  .controls-actions {
    flex-direction: column;
  }

  .btn {
    width: 100%;
    justify-content: center;
  }

  .summary-cards {
    grid-template-columns: 1fr;
  }

  .pagination {
    flex-direction: column;
    align-items: stretch;
  }

  .pagination-controls {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .admin-analytics {
    padding: 20px 12px;
  }

  .page-title {
    font-size: 24px;
  }

  .summary-value {
    font-size: 24px;
  }

  .chart-card,
  .table-card,
  .controls-card {
    padding: 20px;
  }
}
</style>