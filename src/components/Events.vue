<template>
  <div class="page">
    <AppHeader @toggle-search="() => (showSearch = true)" @go-profile="goProfile" />
    <div class="container">
      <header class="page-header">
        <h1 class="page-title">Browse Events</h1>
        <p class="page-subtitle">Discover special happenings and experiences.</p>
      </header>

      <div v-if="loading" class="state state-loading">
        <svg class="spinner" viewBox="0 0 50 50">
          <circle class="path" cx="25" cy="25" r="20" fill="none" stroke-width="5"></circle>
        </svg>
        <p>Loading available events...</p>
      </div>
      <div v-else-if="message" class="state state-error">
        <p>⚠️ Failed to load events. {{ message }}</p>
        <button class="retry-btn" @click="fetchEvents">Try Again</button>
      </div>
      <div v-else-if="events.length === 0" class="state state-empty">
        <p>No events found at the moment. Check back soon!</p>
      </div>

      <div v-else class="controls-card">
        <div class="search-group">
          <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="11" cy="11" r="7"></circle>
            <path d="m21 21-4.3-4.3"></path>
          </svg>
          <input
            v-model="query"
            type="text"
            class="search-input"
            placeholder="Search events by name, type, or location..."
          />
        </div>
        
        <div class="pager">
          <button class="pg-btn" :disabled="page===1" @click="prevPage" aria-label="Previous Page">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="m15 18-6-6 6-6"></path></svg>
          </button>
          <span class="pg-info">Page <strong class="pg-current">{{ page }}</strong> of {{ totalPages }}</span>
          <button class="pg-btn" :disabled="page===totalPages" @click="nextPage" aria-label="Next Page">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="m9 18 6-6-6-6"></path></svg>
          </button>
        </div>
      </div>

      <SearchOverlay v-model="showSearch" :items="events" @select="goToShow" />

      <div v-if="!loading && !message && events.length > 0 && pagedEvents.length === 0" class="state state-no-match">
        <p>No events found matching "{{ query }}". Try a broader search.</p>
      </div>

      <div v-else-if="!message" class="grid">
        <div class="card" v-for="e in pagedEvents" :key="e.id" @click="goToShow(e)">
          <div class="card-poster">
            <img :src="resolvedImage(e.image, e.name)" :alt="e.name" class="poster-img" width="300" height="450" />
            <div class="card-glow"></div>
          </div>
          <div class="card-info">
            <h3 class="card-title">{{ e.name }}</h3>
            <p class="card-meta">{{ e.city || 'Event' }} • {{ formatDate(e.date) }}</p>
            <div class="actions">
              <button class="btn primary-action" @click.stop="book(e)">Book Tickets</button>
              <button class="btn secondary-action" @click.stop="goToShow(e)">Details</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import AppHeader from './AppHeader.vue';
import SearchOverlay from './SearchOverlay.vue';

export default {
  name: 'Events',
  components: { AppHeader, SearchOverlay },
  data() {
    return {
      events: [],
      loading: false,
      message: '',
      showSearch: false,
      placeholder: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='450' viewBox='0 0 300 450'%3E%3Crect fill='%23374151' width='300' height='450'/%3E%3Ctext fill='%239ca3af' font-family='sans-serif' font-size='16' x='50%25' y='50%25' text-anchor='middle' dy='.3em'%3EEvent%3C/text%3E%3C/svg%3E",
      query: '',
      page: 1,
      pageSize: 8
    };
  },
  created() {
    this.fetchEvents();
  },
  computed: {
    filtered() {
      const q = this.query.trim().toLowerCase();
      if (!q) return this.events;
      return this.events.filter(e =>
        (e.name || '').toLowerCase().includes(q) ||
        (e.city || '').toLowerCase().includes(q)
      );
    },
    totalPages() {
      return Math.max(1, Math.ceil(this.filtered.length / this.pageSize));
    },
    pagedEvents() {
      const start = (this.page - 1) * this.pageSize;
      return this.filtered.slice(start, start + this.pageSize);
    }
  },
  watch: {
    query() {
      this.page = 1;
    }
  },
  methods: {
    fetchEvents() {
      this.loading = true;
      this.message = '';
      const token = localStorage.getItem('access_token');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      axios.get('shows', { headers })
        .then(res => {
          const shows = Array.isArray(res.data) ? res.data : [];
          // Filter events
          const eventShows = shows.filter(s => (s.tags || '').toLowerCase().includes('event'));
          // Deduplicate by ID
          const seenIds = new Set();
          this.events = eventShows.filter(s => {
            if (seenIds.has(s.id)) return false;
            seenIds.add(s.id);
            return true;
          }).map(s => ({ id: s.id, name: s.name, city: s.tags, date: s.start_time, image: s.image }));
        })
        .catch(err => {
          this.message = 'Error connecting to the server. Check your connection.';
          console.error(err);
        })
        .finally(() => {
          this.loading = false;
        });
    },
    prevPage() { if (this.page > 1) this.page--; },
    nextPage() { if (this.page < this.totalPages) this.page++; },
    goToShow(item) {
      if (!item || !item.id) return;
      const token = localStorage.getItem('access_token');
      const invalidToken = !token || token === 'null' || token === 'undefined';
      if (invalidToken) {
        this.$router.push({ path: '/login', query: { redirect: `/book/${item.id}` } });
      } else {
        this.$router.push(`/book/${item.id}`);
      }
    },
    book(item) {
      if (!item) return;
      const token = localStorage.getItem('access_token');
      if (!token) {
        this.$router.push({ path: '/login', query: { redirect: `/book/${item.id}` } });
        return;
      }
      this.$router.push(`/book/${item.id}`);
    },
    formatDate(d) {
      if (!d) return '';
      try {
        const dt = new Date(d);
        return dt.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
      } catch {
        return d;
      }
    },
    localAssetFor(name) {
      const key = (name || '').toLowerCase();
      // Event images
      if (key.includes('tech expo')) return 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=500';
      if (key.includes('comic con')) return 'https://images.unsplash.com/photo-1612036782180-6f0b6cd846fe?w=500';
      if (key.includes('food festival')) return 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=500';
      // Concert images (in case they show up)
      if (key.includes('coldplay')) return 'https://images.unsplash.com/photo-1470229722913-7c0e2dbbafd3?w=500';
      if (key.includes('taylor swift')) return 'https://images.unsplash.com/photo-1501386761578-eac5c94b800a?w=500';
      return null;
    },
    resolvedImage(img, name) {
      const local = this.localAssetFor(name);
      if (local) return local;
      if (img && img.startsWith('http')) return img;
      if (img) return `uploads/${encodeURIComponent(img)}`;
      return this.placeholder;
    },
    goProfile() {
      const token = localStorage.getItem('access_token');
      if (token) this.$router.push('/userdashboard');
      else this.$router.push('/login');
    }
  }
};
</script>

<style scoped>
/* Inheriting Colors & Fonts for Consistency */
.page {
  --primary-text: #0f172a;
  --secondary-text: #6b7280;
  --border-color: #e5e7eb;
  --pastel-lilac: #a855f7;
  --font-heading: system-ui, -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Inter', 'Segoe UI', sans-serif;
  --font-body: system-ui, -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', sans-serif;
  
  min-height: 100vh;
  padding: 0 0 40px;
  background:
    radial-gradient(circle at 0% 0%, rgba(217, 212, 241, 0.9) 0, transparent 55%),
    radial-gradient(circle at 100% 0%, rgba(250, 220, 217, 0.9) 0, transparent 55%),
    radial-gradient(circle at 0% 100%, rgba(215, 234, 248, 0.9) 0, transparent 55%),
    #f9fafb;
}

.container {
  max-width: 1180px;
  margin: 0 auto;
  padding: 0 20px;
}

/* ============ HEADER ============ */
.page-header {
  margin: 30px 0;
  padding: 30px 35px;
  background: linear-gradient(135deg, 
    rgba(168, 85, 247, 0.08) 0%,
    rgba(236, 72, 153, 0.06) 50%,
    rgba(59, 130, 246, 0.08) 100%);
  border-radius: 20px;
  border: 1px solid rgba(168, 85, 247, 0.12);
}
.page-title {
  font-family: var(--font-heading);
  font-size: 34px;
  font-weight: 800;
  letter-spacing: -0.5px;
  background: linear-gradient(135deg, var(--pastel-lilac) 0%, #ec4899 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 8px;
}
.page-subtitle {
  color: var(--secondary-text);
  font-size: 16px;
  margin: 0;
}

/* ============ CONTROLS CARD (Search & Pager) ============ */
.controls-card {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 30px;
  padding: 20px 25px;
  background: rgba(255, 255, 255, 0.96);
  border-radius: 18px;
  box-shadow: 0 10px 30px rgba(148, 163, 184, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.9);
}

.search-group {
  flex: 1;
  max-width: 400px;
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 12px;
  width: 20px;
  height: 20px;
  color: var(--secondary-text);
  opacity: 0.7;
}

.search-input {
  width: 100%;
  padding: 10px 15px 10px 40px;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  font-size: 15px;
  color: var(--primary-text);
  background-color: #fcfdfe;
  transition: all 0.3s ease;
}

.search-input:focus {
  border-color: var(--pastel-lilac);
  box-shadow: 0 0 0 2px rgba(168, 85, 247, 0.2);
  outline: none;
  background-color: white;
}

/* --- Pager --- */
.pager {
  display: flex;
  align-items: center;
  gap: 10px;
}

.pg-btn {
  width: 38px;
  height: 38px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--border-color);
  background: white;
  color: var(--secondary-text);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.pg-btn:hover:not(:disabled) {
  background: var(--pastel-lilac);
  color: white;
  border-color: var(--pastel-lilac);
  box-shadow: 0 4px 10px rgba(168, 85, 247, 0.3);
}

.pg-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pg-info {
  color: var(--secondary-text);
  font-size: 14px;
  font-weight: 500;
}

.pg-current {
  color: var(--primary-text);
  font-weight: 700;
}

/* ============ STATES ============ */
.state {
  padding: 40px;
  text-align: center;
  border-radius: 18px;
  margin-top: 20px;
  font-size: 16px;
  font-weight: 500;
  background-color: #f0f0f5;
  border: 1px solid var(--border-color);
}

.state-error {
  background-color: #ffe4e6;
  color: #c0392b;
  border-color: #f0c0c0;
}

.retry-btn {
  margin-top: 15px;
  padding: 8px 15px;
  border: none;
  border-radius: 8px;
  background: #f7a8b9;
  color: white;
  cursor: pointer;
  font-weight: 600;
}

.state-no-match {
  background-color: #fff8e1;
  border-color: #fae3ac;
  color: #b38800;
}

/* Spinner */
.spinner {
  animation: rotate 2s linear infinite;
  margin: -15px auto 10px;
  width: 30px;
  height: 30px;
}

.spinner .path {
  stroke: var(--pastel-lilac);
  stroke-linecap: round;
  animation: dash 1.5s ease-in-out infinite;
}

@keyframes rotate {
  100% { transform: rotate(360deg); }
}
@keyframes dash {
  0% { stroke-dasharray: 1, 150; stroke-dashoffset: 0; }
  50% { stroke-dasharray: 90, 150; stroke-dashoffset: -35; }
  100% { stroke-dasharray: 90, 150; stroke-dashoffset: -124; }
}


/* ============ GRID & CARD ============ */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 28px;
}

.card {
  cursor: pointer;
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 12px 30px rgba(148, 163, 184, 0.1);
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 50px rgba(168, 85, 247, 0.25);
}

.card-poster {
  position: relative;
  aspect-ratio: 2 / 3;
  overflow: hidden;
  background: #f0f4f7;
}

.poster-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.4s ease;
}

.card:hover .poster-img {
  transform: scale(1.06);
}

.card-glow {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 90% 100%, rgba(168, 85, 247, 0.45), transparent 65%);
  mix-blend-mode: overlay;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.card:hover .card-glow {
  opacity: 1;
}

.card-info {
  padding: 18px;
}

.card-title {
  font-family: var(--font-heading);
  font-size: 18px;
  font-weight: 700;
  color: var(--primary-text);
  margin: 0 0 6px 0;
  line-height: 1.3;
}

.card-meta {
  font-size: 14px;
  color: var(--secondary-text);
  margin: 0 0 15px 0;
}

/* --- Actions --- */
.actions {
  display: flex;
  gap: 8px;
}

.btn {
  font-size: 14px;
  font-weight: 600;
  padding: 10px 15px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}

.primary-action {
  flex: 2;
  background: var(--pastel-lilac);
  color: white;
  box-shadow: 0 4px 12px rgba(168, 85, 247, 0.3);
}

.primary-action:hover {
  background: #8b5aa0;
}

.secondary-action {
  flex: 1;
  background: rgba(168, 85, 247, 0.1);
  color: var(--pastel-lilac);
  border: 1px solid rgba(168, 85, 247, 0.3);
}

.secondary-action:hover {
  background: rgba(168, 85, 247, 0.2);
}


/* ============ RESPONSIVE ============ */
@media (max-width: 992px) {
  .grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  }
}

@media (max-width: 768px) {
  .controls-card {
    flex-direction: column;
    align-items: stretch;
    padding: 15px;
  }
  .search-group {
    max-width: 100%;
  }
  .pager {
    width: 100%;
    justify-content: space-between;
  }
  .grid {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 18px;
  }
  .card-title {
    font-size: 16px;
  }
  .actions {
    flex-direction: column;
  }
  .btn {
    flex: none;
    width: 100%;
  }
}
</style>

