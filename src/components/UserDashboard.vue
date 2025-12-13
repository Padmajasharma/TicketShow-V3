<template>
  <div class="dashboard">
    <AppHeader @toggle-search="() => {}" @go-profile="Profile" /> 
    
    <section class="welcome-section">
      <div class="container">
        <div class="welcome-card">
          <div class="welcome-left">
            <span class="welcome-badge">Dashboard</span>
            <h1 class="welcome-title">Welcome back <span class="wave">👋</span></h1>
            <p class="welcome-subtitle">
              Search theatres & shows, check availability, and book your next experience.
            </p>
          </div>
          
        </div>
      </div>
    </section>

    <div v-if="message" class="dashboard-message container" :class="messageType" @click="clearMessage">
      <span class="message-icon">{{ messageType === 'success' ? '✓' : '⚠' }}</span>
      {{ message }}
      <span class="close-msg">×</span>
    </div>

    <section class="search-section">
      <div class="section-container container">
        <div class="search-card card">
          <div class="card-header">
            <div class="header-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="11" cy="11" r="8"></circle>
                <path d="m21 21-4.3-4.3"></path>
              </svg>
            </div>
            <div class="header-text">
              <h2>Quick Search</h2>
              <p>Find shows by name, location, tags, or rating.</p>
            </div>
          </div>

          <div class="search-controls">
            <div class="field search-field">
              <label>Search query</label>
              <div class="input-wrapper">
                <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="11" cy="11" r="8"></circle>
                  <path d="m21 21-4.3-4.3"></path>
                </svg>
                <input
                  type="text"
                  v-model="searchQuery"
                  @input="performSearch"
                  placeholder="e.g., 'PVR', 'comedy', '4.5'..."
                />
              </div>
            </div>

            <div class="field filter-field">
              <label>Search by</label>
              <div class="select-wrapper">
                <select v-model="searchOption">
                  <option value="showName">Show Name</option>
                  <option value="theatreName">Theatre Name</option>
                  <option value="theatrePlace">Theatre Place</option>
                  <option value="showTags">Show Tags</option>
                  <option value="showRating">Show Rating</option>
                </select>
                <svg class="select-arrow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="m6 9 6 6 6-6"></path>
                </svg>
              </div>
            </div>
          </div>

          <div v-if="searchResults.length > 0" class="search-results">
            <div class="search-results-header">
              <h3>Results</h3>
              <span class="results-badge badge">{{ searchResults.length }} found</span>
            </div>

            <div class="results-grid">
              <div v-for="result in searchResults" :key="result.id" class="result-card">
                <div class="result-main">
                  <div class="result-title">{{ result.name }}</div>
                  <div class="result-sub">
                    <template v-if="result.place">{{ result.place }}</template>
                    <template v-else-if="result.rating">Rating: {{ result.rating }}</template>
                    <template v-else-if="result.tags">{{ result.tags }}</template>
                  </div>
                </div>
                <div class="result-tag">{{ getResultTag(result) }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="shows-section">
      <div class="section-container container">
        <div class="shows-header">
          <div class="shows-header-content">
            <h2>Shows Available</h2>
            <p v-if="shows.length" class="shows-subtitle">
              You can currently book <strong>{{ shows.length }}</strong> featured shows.
            </p>
            <p v-else class="shows-subtitle">No featured shows available yet. Check back soon!</p>
          </div>
        </div>

        <div v-if="shows.length > 0" class="shows-grid">
          <div v-for="show in shows" :key="show.id" class="show-card card">
            <div class="show-media" @click="goToShow(show)">
              <img 
                :src="show.image" 
                class="show-image" 
                :alt="show.name"
                @error="handleImageError($event)"
              />
              <div class="show-overlay"></div>
              <div class="capacity-pill" :class="{ 'capacity-zero': show.capacity === 0 }">
                {{ show.capacity > 0 ? show.capacity + ' seats left' : 'Houseful' }}
              </div>
              <span v-if="show.rating" class="rating-badge">★ {{ show.rating.toFixed(1) }}</span>
            </div>

            <div class="show-content">
              <h3 class="show-title">{{ show.name }}</h3>

              <div class="show-meta">
                <div class="meta-item">
                  <div class="meta-text">
                    <span class="meta-label">Theatre</span>
                    <span class="meta-value">{{ getTheatreName(show.theatre_id) }}</span>
                  </div>
                </div>
                <div class="meta-item">
                  <div class="meta-text">
                    <span class="meta-label">Location</span>
                    <span class="meta-value">{{ getTheatrePlace(show.theatre_id) || 'N/A' }}</span>
                  </div>
                </div>
                <div class="meta-item">
                  <div class="meta-text">
                    <span class="meta-label">Time</span>
                    <span class="meta-value">{{ show.start_time }}</span>
                  </div>
                </div>
                <div class="meta-item">
                  <div class="meta-text">
                    <span class="meta-label">Price</span>
                    <span class="meta-value">₹{{ show.ticket_price }}</span>
                  </div>
                </div>
              </div>

              <div class="show-tags" v-if="show.tags">
                <span class="tag-chip" v-for="tag in show.tags.split(',')" :key="tag.trim()">
                  {{ tag.trim() }}
                </span>
              </div>

              <div class="show-footer">
                <button
                  v-if="!selectedShowId || selectedShowId !== show.id"
                  :disabled="show.capacity === 0"
                  @click="goToShow(show)"
                  class="btn btn-book primary-action"
                >
                  {{ show.capacity > 0 ? 'Book Now' : 'Sold Out' }}
                </button>
              </div>

              <div v-if="show.id === selectedShowId" class="booking-panel">
                <div class="booking-header">
                  <span>Confirm Details</span>
                </div>
                
                <div class="rating-row">
                  <label for="rating">Your Rating (1-5)</label>
                  <div class="star-rating">
                    <input
                      type="number"
                      id="rating"
                      v-model="rating"
                      min="1"
                      max="5"
                      class="rating-input"
                    />
                  </div>
                </div>

                <form @submit.prevent="bookTickets(show.id)" class="booking-form">
                  <div class="field">
                    <label for="numberOfTickets">Number of tickets (Max {{ show.capacity }})</label>
                    <input
                      type="number"
                      id="numberOfTickets"
                      v-model="numberOfTickets"
                      min="1"
                      :max="show.capacity"
                      required
                    />
                  </div>
                  <div class="booking-actions">
                    <button type="submit" class="btn btn-confirm">✓ Confirm Booking</button>
                    <button type="button" @click="cancelBooking" class="btn btn-cancel">
                      Cancel
                    </button>
                  </div>
                </form>
              </div>

              <div v-if="bookingStatus && show.id === selectedShowId" class="booking-status">
                Tickets booked for <strong>{{ show.name }}</strong>. Thank you!
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- My Bookings Section -->
    <section class="bookings-section">
      <div class="section-container container">
        <div class="section-header">
          <h2>My Bookings</h2>
          <p class="section-subtitle" v-if="bookedShows.length">
            You have <strong>{{ bookedShows.length }}</strong> booked shows. Rate them below!
          </p>
          <p class="section-subtitle" v-else>You haven't booked any shows yet.</p>
        </div>

        <!-- Stats Cards -->
        <div v-if="stats.total_bookings > 0" class="stats-row">
          <div class="stat-card">
            <span class="stat-value">{{ stats.total_bookings }}</span>
            <span class="stat-label">Shows Booked</span>
          </div>
          <div class="stat-card">
            <span class="stat-value">{{ stats.total_tickets }}</span>
            <span class="stat-label">Total Tickets</span>
          </div>
          <div class="stat-card">
            <span class="stat-value">₹{{ stats.total_spent }}</span>
            <span class="stat-label">Total Spent</span>
          </div>
        </div>

        <!-- Booked Shows List -->
        <div v-if="bookedShows.length > 0" class="booked-shows-list">
          <div v-for="booking in bookedShows" :key="booking.show_id" class="booked-show-card">
            <div class="booked-show-image">
              <img :src="booking.image || noImagePlaceholder" :alt="booking.show_name" @error="handleImageError($event)" />
            </div>
            <div class="booked-show-info">
              <h3 class="booked-show-title">{{ booking.show_name }}</h3>
              <div class="booked-show-meta">
                <span class="meta-tag">{{ booking.ticket_count }} ticket{{ booking.ticket_count > 1 ? 's' : '' }}</span>
                <span class="meta-tag">₹{{ booking.ticket_price * booking.ticket_count }}</span>
              </div>
              <p class="booked-show-time">{{ formatBookingDate(booking.show_start_time) }}</p>
              <div v-if="booking.tags" class="booked-show-tags">
                <span v-for="tag in booking.tags.split(',')" :key="tag" class="mini-tag">{{ tag.trim() }}</span>
              </div>
              <div class="booked-show-actions">
                <button v-if="booking.ticket_count && booking.ticket_count > 0" class="btn btn-download" @click="downloadTickets(booking)">
                  Download Tickets
                </button>
              </div>
            </div>
            <div class="booked-show-rating">
              <div class="rating-label">Your Rating</div>
              <div class="star-rating-input">
                <button 
                  v-for="star in 5" 
                  :key="star" 
                  class="star-btn"
                  :class="{ 'active': (ratingInProgress[booking.show_id] || booking.user_rating || 0) >= star }"
                  @click="setRating(booking.show_id, star)"
                >
                  ★
                </button>
              </div>
              <button 
                v-if="ratingInProgress[booking.show_id] && ratingInProgress[booking.show_id] !== booking.user_rating"
                class="submit-rating-btn"
                @click="submitRating(booking.show_id)"
              >
                Save
              </button>
              <span v-else-if="booking.user_rating" class="rating-saved">Rated {{ booking.user_rating }}/5</span>
            </div>
          </div>
        </div>

        <div v-else class="empty-bookings">
          <p>No bookings yet. Browse shows above and book your first experience!</p>
        </div>
      </div>
    </section>
  </div>
</template>
<script>
import AppHeader from './AppHeader.vue';
import axios from 'axios';
import { isAuthenticated } from '@/utils/auth';

export default {
  name: 'UserDashboard',
  components: { AppHeader },
  data() {
    return {
      noImagePlaceholder: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='450' viewBox='0 0 300 450'%3E%3Crect fill='%23374151' width='300' height='450'/%3E%3Ctext fill='%239ca3af' font-family='sans-serif' font-size='16' x='50%25' y='50%25' text-anchor='middle' dy='.3em'%3ENo Image%3C/text%3E%3C/svg%3E",
      message: '',
      messageType: 'success',
      searchQuery: '',
      searchOption: 'showName',
      searchResults: [],
      shows: [],
      theatres: [], 
      selectedShowId: null,
      rating: 5,
      numberOfTickets: 1,
      bookingStatus: false,
      showBookingForm: false,
      isLoading: false,
      // Bookings data
      bookedShows: [],
      stats: { total_bookings: 0, total_tickets: 0, total_spent: 0 },
      ratingInProgress: {},
    };
  },
  created() {
    this.fetchData();
    this.fetchBookings();
  },
  methods: {
    async fetchData() {
      const token = localStorage.getItem('access_token');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      
      try {
        // Fetch shows (use axios so requests go to configured backend baseURL)
        const showsResp = await axios.get('/shows', { headers });
        const showsData = showsResp.data;
        
        if (Array.isArray(showsData)) {
          this.shows = showsData.map(s => ({
            id: s.id,
            name: s.name,
            rating: s.rating || null,
            tags: s.tags || '',
            ticket_price: s.ticket_price,
            start_time: this.formatDateTime(s.start_time),
            end_time: this.formatDateTime(s.end_time),
            theatre_id: s.theatre_id,
            image: s.image ? s.image : this.noImagePlaceholder,
            capacity: s.capacity ?? 0,
          }));
        }

        // Fetch theatres
        const theatresResp = await axios.get('/theatres', { headers });
        const theatresData = theatresResp.data;
        if (Array.isArray(theatresData)) {
          this.theatres = theatresData;
        }
      } catch (err) {
        console.error('Error fetching data:', err);
        this.shows = [];
      }
    },

    formatDateTime(isoString) {
      if (!isoString) return 'N/A';
      const date = new Date(isoString);
      return date.toLocaleString('en-IN', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    },

    getTheatreName(theatreId) {
      const theatre = this.theatres.find(t => t.id === theatreId);
      return theatre ? theatre.name : `Venue #${theatreId}`;
    },

    getTheatrePlace(theatreId) {
      const theatre = this.theatres.find(t => t.id === theatreId);
      return theatre ? theatre.place : '';
    },

    Profile() {
      this.$router.push('/userprofile');
    },

    logout() {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_id');
      localStorage.removeItem('role');
      this.$router.push('/login');
    },

    async performSearch() {
      // ... (Keep existing performSearch logic)
      const q = this.searchQuery.trim().toLowerCase();
      if (!q) { 
        this.searchResults = []; 
        return; 
      }

      const token = localStorage.getItem('access_token');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};

      try {
        if (this.searchOption === 'showName') {
          // Search shows by name locally
          this.searchResults = this.shows
            .filter(s => (s.name || '').toLowerCase().includes(q))
            .map(s => ({
              id: s.id,
              name: s.name,
              tags: s.tags,
              rating: s.rating?.toFixed(1),
              type: 'show'
            }));
          return;
        }
        if (this.searchOption === 'theatreName') {
          // Search theatres by name via API
          const res = await axios.get(`/search/theatres?name=${encodeURIComponent(q)}`, { headers });
          const data = res.data;
          this.searchResults = (data || []).map(t => ({
            id: t.id,
            name: t.name,
            place: t.place,
            type: 'theatre'
          }));
        } else if (this.searchOption === 'theatrePlace') {
          // Search theatres by place via API
          const res = await axios.get(`/search/theatres?place=${encodeURIComponent(q)}`, { headers });
          const data = res.data;
          this.searchResults = (data || []).map(t => ({
            id: t.id,
            name: t.name,
            place: t.place,
            type: 'theatre'
          }));
        } else if (this.searchOption === 'showTags') {
          // Search shows by tags via API
          const res = await axios.get(`/search/shows?tags=${encodeURIComponent(q)}`, { headers });
          const data = res.data;
          this.searchResults = (data || []).map(s => ({
            id: s.id,
            name: s.name,
            tags: s.tags,
            type: 'show'
          }));
        } else if (this.searchOption === 'showRating') {
          // Search shows by rating via API
          const res = await axios.get(`/search/shows?rating=${encodeURIComponent(q)}`, { headers });
          const data = res.data;
          this.searchResults = (data || []).map(s => ({
            id: s.id,
            name: s.name,
            rating: s.rating?.toFixed(1),
            type: 'show'
          }));
        }
      } catch (err) {
        console.error('Search error:', err);
        this.searchResults = [];
      }
    },

    async bookTickets(showId) {
      // ... (Keep existing bookTickets logic)
      const token = localStorage.getItem('access_token');
      if (!token) {
        this.message = 'Please login to book tickets';
        this.messageType = 'error';
        return;
      }

      const show = this.shows.find(s => s.id === showId);
      if (!show) return;

      if (this.numberOfTickets > show.capacity) {
        this.message = `Only ${show.capacity} seats available!`;
        this.messageType = 'error';
        return;
      }

      this.isLoading = true;
      try {
        const payload = {
          number_of_tickets: this.numberOfTickets,
          rating: this.rating
        };
        const res = await axios.post(`/bookshows/${showId}/book`, payload, {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          }
        });
        const data = res.data;
        if (res.status >= 200 && res.status < 300) {
          this.bookingStatus = true;
          this.message = data.message || `Successfully booked ${this.numberOfTickets} tickets for ${show.name}!`;
          this.messageType = 'success';
          
          // Update local capacity
          show.capacity -= this.numberOfTickets;
          
          // Refresh bookings to show new booking
          this.fetchBookings();
          
          // Reset form after delay
          setTimeout(() => {
            this.selectedShowId = null;
            this.numberOfTickets = 1;
            this.rating = 5;
            this.bookingStatus = false;
            this.showBookingForm = false;
          }, 3000);
        } else {
          this.message = data.message || 'Booking failed. Please try again.';
          this.messageType = 'error';
        }
      } catch (err) {
        console.error('Booking error:', err);
        this.message = 'Network error. Please try again.';
        this.messageType = 'error';
      } finally {
        this.isLoading = false;
      }
    },

    cancelBooking() {
      this.bookingStatus = false;
      this.selectedShowId = null;
      this.showBookingForm = false;
      this.numberOfTickets = 1;
      this.rating = 5;
    },

    goToShow(show) {
      console.log('isAuthenticated:', isAuthenticated()); // Debug log
      if (!isAuthenticated()) {
        this.$router.push({ path: '/login', query: { redirect: `/book/${show.id}` } });
      } else {
        this.$router.push(`/book/${show.id}`);
      }
    },

    getResultIcon(result) {
      return '';
    },

    getResultTag(result) {
      if (this.searchOption === 'theatreName' || this.searchOption === 'theatrePlace') return 'VENUE';
      return 'SHOW';
    },

    clearMessage() {
      this.message = '';
    },

    handleImageError(event) {
      event.target.src = this.noImagePlaceholder;
    },

    async fetchBookings() {
      const token = localStorage.getItem('access_token');
      if (!token) return;

      try {
        const res = await axios.get('/userprofile', {
          headers: { Authorization: `Bearer ${token}` }
        });
        const data = res.data;
        if (data.booked_shows) {
          this.bookedShows = data.booked_shows;
        }
        if (data.stats) {
          this.stats = data.stats;
        }
      } catch (err) {
        console.error('Error fetching bookings:', err);
      }
    },

    formatBookingDate(dateStr) {
      if (!dateStr) return 'N/A';
      const date = new Date(dateStr);
      return date.toLocaleDateString('en-IN', {
        weekday: 'short',
        day: 'numeric',
        month: 'short',
        hour: '2-digit',
        minute: '2-digit'
      });
    },

    setRating(showId, rating) {
      this.ratingInProgress = { ...this.ratingInProgress, [showId]: rating };
    },

    async submitRating(showId) {
      const token = localStorage.getItem('access_token');
      if (!token) {
        this.message = 'Please login to rate shows';
        this.messageType = 'error';
        return;
      }

      const rating = this.ratingInProgress[showId];
      if (!rating) return;

      try {
        const res = await axios.post(`/rate/${showId}`, { rating }, {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          }
        });
        const data = res.data;
        if (res.status >= 200 && res.status < 300) {
          // Update local state
          const booking = this.bookedShows.find(b => b.show_id === showId);
          if (booking) {
            booking.user_rating = rating;
          }
          delete this.ratingInProgress[showId];
          this.message = 'Rating saved!';
          this.messageType = 'success';
        } else {
          this.message = data.message || 'Failed to save rating';
          this.messageType = 'error';
        }
      } catch (err) {
        console.error('Rating error:', err);
        this.message = 'Network error';
        this.messageType = 'error';
      }
    }

    ,
    async downloadTickets(booking) {
      const token = localStorage.getItem('access_token');
      if (!token) {
        this.message = 'Please login to download tickets';
        this.messageType = 'error';
        return;
      }
      const headers = { Authorization: `Bearer ${token}` };
      try {
        // If ticket_ids not already present, fetch user's tickets and filter by show
        let ticketIds = booking.ticket_ids && booking.ticket_ids.length ? booking.ticket_ids : null;
        if (!ticketIds) {
          const resp = await axios.get('/tickets', { headers });
          const allTickets = resp.data.tickets || [];
          ticketIds = allTickets.filter(t => t.show_id === booking.show_id).map(t => t.id);
          // cache on booking object for future clicks
          booking.ticket_ids = ticketIds;
        }
        if (!ticketIds || ticketIds.length === 0) {
          this.message = 'No tickets found to download for this booking';
          this.messageType = 'error';
          return;
        }

        for (const tid of ticketIds) {
          const res = await axios.get(`/tickets/${tid}/download`, { headers, responseType: 'blob' });
          const blob = new Blob([res.data], { type: 'application/pdf' });
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `ticket_${tid}.pdf`;
          document.body.appendChild(a);
          a.click();
          a.remove();
          window.URL.revokeObjectURL(url);
        }
      } catch (err) {
        console.error('Failed to download tickets:', err);
        this.message = 'Failed to download tickets';
        this.messageType = 'error';
      }
    }
  }
};
</script>
<style scoped>
/* ============================== */
/* VARIABLES & BASE */
/* ============================== */
.dashboard {
  --primary-text: #0f172a;
  --secondary-text: #6b7280;
  --border-color: #e5e7eb;
  --accent: #a855f7;
  --accent-light: rgba(168, 85, 247, 0.1);
  --bg: #f8fafc;
  --card-bg: #ffffff;
  --radius: 16px;
  --radius-sm: 10px;
  --shadow: 0 4px 20px rgba(15, 23, 42, 0.08);
  --shadow-lg: 0 10px 40px rgba(15, 23, 42, 0.12);
  
  min-height: 100vh;
  background:
    radial-gradient(circle at 0% 0%, rgba(217, 212, 241, 0.9) 0, transparent 55%),
    radial-gradient(circle at 100% 0%, rgba(250, 220, 217, 0.9) 0, transparent 55%),
    radial-gradient(circle at 0% 100%, rgba(215, 234, 248, 0.9) 0, transparent 55%),
    #f9fafb;
  padding-bottom: 60px;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  color: var(--primary-text);
}

.container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 20px;
}

/* ============================== */
/* WELCOME SECTION */
/* ============================== */
.welcome-section {
  padding: 24px 0;
}

.welcome-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 24px 32px;
  background: var(--card-bg);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  border: 1px solid var(--border-color);
}

.welcome-badge {
  display: inline-block;
  padding: 4px 12px;
  background: var(--accent-light);
  color: var(--accent);
  font-size: 12px;
  font-weight: 600;
  border-radius: 20px;
  margin-bottom: 8px;
}

.welcome-title {
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 6px;
  color: var(--primary-text);
}

.wave {
  display: inline-block;
  animation: wave 2s ease-in-out infinite;
}

@keyframes wave {
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(20deg); }
  75% { transform: rotate(-10deg); }
}

.welcome-subtitle {
  font-size: 14px;
  color: var(--secondary-text);
  margin: 0;
}

.welcome-right {
  display: flex;
  gap: 10px;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  border-radius: var(--radius-sm);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.2s ease;
}

.profile-btn {
  background: var(--accent);
  color: white;
}

.profile-btn:hover {
  background: #9333ea;
}

.logout-btn {
  background: var(--card-bg);
  color: var(--secondary-text);
  border-color: var(--border-color);
}

.logout-btn:hover {
  background: #fef2f2;
  color: #dc2626;
  border-color: #fecaca;
}

/* ============================== */
/* MESSAGE */
/* ============================== */
.dashboard-message {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border-radius: var(--radius-sm);
  font-size: 14px;
  margin-bottom: 20px;
  cursor: pointer;
}

.dashboard-message.success {
  background: #ecfdf5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}

.dashboard-message.error {
  background: #fef2f2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.close-msg {
  margin-left: auto;
  opacity: 0.5;
}

/* ============================== */
/* SEARCH SECTION */
/* ============================== */
.search-section {
  padding: 0 0 30px;
}

.card {
  background: var(--card-bg);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  border: 1px solid var(--border-color);
  padding: 24px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.header-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--accent-light);
  color: var(--accent);
  border-radius: 10px;
}

.card-header h2 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.card-header p {
  font-size: 13px;
  color: var(--secondary-text);
  margin: 2px 0 0;
}

.search-controls {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.field {
  flex: 1;
  min-width: 200px;
}

.field label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--secondary-text);
  margin-bottom: 6px;
}

.input-wrapper {
  position: relative;
}

.input-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--secondary-text);
}

.field input,
.field select {
  width: 100%;
  padding: 10px 12px 10px 40px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  font-size: 14px;
  background: var(--card-bg);
  transition: all 0.2s ease;
}

.field select {
  padding-left: 12px;
  cursor: pointer;
}

.field input:focus,
.field select:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-light);
}

.select-wrapper {
  position: relative;
}

.select-arrow {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
  color: var(--secondary-text);
}

/* Search Results */
.search-results {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}

.search-results-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.search-results-header h3 {
  font-size: 15px;
  font-weight: 600;
  margin: 0;
}

.results-badge {
  padding: 3px 10px;
  background: var(--accent-light);
  color: var(--accent);
  font-size: 12px;
  font-weight: 500;
  border-radius: 12px;
}

.results-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.result-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: var(--bg);
  border-radius: var(--radius-sm);
  border: 1px solid transparent;
  transition: all 0.2s ease;
}

.result-card:hover {
  border-color: var(--accent);
  background: var(--card-bg);
}

.result-title {
  font-size: 14px;
  font-weight: 500;
}

.result-sub {
  font-size: 12px;
  color: var(--secondary-text);
  margin-top: 2px;
}

.result-tag {
  padding: 4px 10px;
  background: var(--border-color);
  color: var(--secondary-text);
  font-size: 10px;
  font-weight: 600;
  border-radius: 6px;
}

/* ============================== */
/* SHOWS SECTION */
/* ============================== */
.shows-section {
  padding: 10px 0;
}

.shows-header {
  margin-bottom: 24px;
}

.shows-header h2 {
  font-size: 22px;
  font-weight: 700;
  margin: 0 0 6px;
}

.shows-subtitle {
  font-size: 14px;
  color: var(--secondary-text);
  margin: 0;
}

.shows-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}

.show-card {
  padding: 0;
  overflow: hidden;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.show-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.show-media {
  position: relative;
  height: 180px;
  overflow: hidden;
  cursor: pointer;
}

.show-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.show-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(0,0,0,0.4), transparent);
}

.capacity-pill {
  position: absolute;
  bottom: 12px;
  left: 12px;
  padding: 6px 12px;
  background: rgba(255,255,255,0.95);
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  color: var(--primary-text);
}

.capacity-zero {
  background: #fee2e2;
  color: #dc2626;
}

.rating-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  padding: 4px 10px;
  background: rgba(0,0,0,0.7);
  color: #fbbf24;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
}

.show-content {
  padding: 20px;
}

.show-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 12px;
}

.show-meta {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 14px;
}

.meta-item {
  padding: 10px;
  background: var(--bg);
  border-radius: var(--radius-sm);
}

.meta-label {
  display: block;
  font-size: 11px;
  color: var(--secondary-text);
  margin-bottom: 2px;
}

.meta-value {
  font-size: 13px;
  font-weight: 500;
}

.show-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 16px;
}

.tag-chip {
  padding: 4px 10px;
  background: var(--accent-light);
  color: var(--accent);
  font-size: 12px;
  font-weight: 500;
  border-radius: 6px;
}

.show-footer {
  margin-top: 4px;
}

.btn-book {
  width: 100%;
  padding: 12px;
  background: var(--accent);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-book:hover:not(:disabled) {
  background: #9333ea;
}

.btn-book:disabled {
  background: #d1d5db;
  cursor: not-allowed;
}

/* ============================== */
/* BOOKING PANEL */
/* ============================== */
.booking-panel {
  margin-top: 16px;
  padding: 16px;
  background: var(--bg);
  border-radius: var(--radius-sm);
}

.booking-header {
  font-size: 15px;
  font-weight: 600;
  color: var(--accent);
  margin-bottom: 14px;
}

.rating-row {
  margin-bottom: 14px;
}

.rating-row label {
  display: block;
  font-size: 13px;
  color: var(--secondary-text);
  margin-bottom: 6px;
}

.rating-input {
  width: 80px;
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  font-size: 14px;
}

.booking-form .field {
  margin-bottom: 14px;
}

.booking-form input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  font-size: 14px;
}

.booking-actions {
  display: flex;
  gap: 10px;
}

.btn-confirm {
  flex: 1;
  padding: 10px 16px;
  background: #10b981;
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
}

.btn-confirm:hover {
  background: #059669;
}

.btn-cancel {
  padding: 10px 16px;
  background: var(--card-bg);
  color: var(--secondary-text);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  font-size: 14px;
  cursor: pointer;
}

.btn-cancel:hover {
  background: #fef2f2;
  color: #dc2626;
  border-color: #fecaca;
}

.booking-status {
  margin-top: 14px;
  padding: 12px;
  background: #ecfdf5;
  color: #065f46;
  border-radius: var(--radius-sm);
  font-size: 14px;
  text-align: center;
}

/* ============================== */
/* MY BOOKINGS SECTION */
/* ============================== */
.bookings-section {
  padding: 40px 0 20px;
  border-top: 1px solid var(--border-color);
  margin-top: 40px;
}

.section-header {
  margin-bottom: 24px;
}

.section-header h2 {
  font-size: 22px;
  font-weight: 700;
  margin: 0 0 6px;
}

.section-subtitle {
  font-size: 14px;
  color: var(--secondary-text);
  margin: 0;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 28px;
}

.stat-card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  padding: 20px;
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 28px;
  font-weight: 700;
  color: var(--accent);
}

.stat-label {
  display: block;
  font-size: 13px;
  color: var(--secondary-text);
  margin-top: 4px;
}

.booked-shows-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.booked-show-card {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  transition: all 0.2s ease;
}

.booked-show-card:hover {
  box-shadow: var(--shadow);
}

.booked-show-image {
  flex-shrink: 0;
  width: 80px;
  height: 100px;
  border-radius: var(--radius-sm);
  overflow: hidden;
}

.booked-show-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.booked-show-info {
  flex: 1;
  min-width: 0;
}

.booked-show-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.booked-show-meta {
  display: flex;
  gap: 8px;
  margin-bottom: 6px;
}

.meta-tag {
  padding: 3px 8px;
  background: var(--accent-light);
  color: var(--accent);
  font-size: 12px;
  font-weight: 500;
  border-radius: 6px;
}

.booked-show-time {
  font-size: 13px;
  color: var(--secondary-text);
  margin: 0 0 8px;
}

.booked-show-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.mini-tag {
  padding: 2px 6px;
  background: var(--bg);
  color: var(--secondary-text);
  font-size: 11px;
  border-radius: 4px;
}

.booked-show-rating {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-width: 100px;
}

.rating-label {
  font-size: 11px;
  color: var(--secondary-text);
  margin-bottom: 6px;
}

.star-rating-input {
  display: flex;
  gap: 2px;
}

.star-btn {
  background: none;
  border: none;
  font-size: 20px;
  color: #d1d5db;
  cursor: pointer;
  padding: 2px;
  transition: all 0.15s ease;
}

.star-btn:hover,
.star-btn.active {
  color: #fbbf24;
  transform: scale(1.1);
}

.submit-rating-btn {
  margin-top: 8px;
  padding: 4px 12px;
  background: var(--accent);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
}

.submit-rating-btn:hover {
  background: #9333ea;
}

.rating-saved {
  margin-top: 6px;
  font-size: 11px;
  color: #10b981;
}

.empty-bookings {
  padding: 40px;
  text-align: center;
  color: var(--secondary-text);
  background: var(--bg);
  border-radius: var(--radius);
}

/* ============================== */
/* RESPONSIVE */
/* ============================== */
@media (max-width: 768px) {
  .welcome-card {
    flex-direction: column;
    align-items: flex-start;
    padding: 20px;
  }
  
  .welcome-right {
    width: 100%;
    margin-top: 16px;
  }
  
  .action-btn {
    flex: 1;
    justify-content: center;
  }
  
  .search-controls {
    flex-direction: column;
  }
  
  .shows-grid {
    grid-template-columns: 1fr;
  }
  
  .show-meta {
    grid-template-columns: 1fr;
  }

  .stats-row {
    grid-template-columns: 1fr;
  }

  .booked-show-card {
    flex-direction: column;
  }

  .booked-show-image {
    width: 100%;
    height: 150px;
  }

  .booked-show-rating {
    flex-direction: row;
    justify-content: space-between;
    width: 100%;
    padding-top: 12px;
    border-top: 1px solid var(--border-color);
  }
}
</style>