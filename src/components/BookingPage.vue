<template>
  <div class="booking-page">
    <AppHeader @toggle-search="() => {}" @go-profile="goToProfile" />
    
    <!-- Back button and title -->
    <div class="page-header">
      <div class="container">
        <button @click="goBack" class="btn-back">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="m15 18-6-6 6-6"></path>
          </svg>
          Back
        </button>
        <h1 class="page-title">Book Tickets</h1>
      </div>
    </div>

    <main class="booking-main">
      <div class="container">
        <!-- Show Info Card -->
        <div class="show-info-card" v-if="show">
          <div class="show-poster">
            <img :src="show.image || placeholder" :alt="show.name" @error="handleImageError" />
          </div>
          <div class="show-details">
            <h2 class="show-title">{{ show.name }}</h2>
            <p class="show-meta">
              <span class="tag">{{ show.tags || 'General' }}</span>
              <span class="rating" v-if="show.rating">★ {{ show.rating }}</span>
              <span class="runtime" v-if="show.runtime">{{ show.runtime }} min</span>
            </p>
            <p class="show-overview" v-if="show.overview">{{ truncateText(show.overview, 150) }}</p>
            <p class="show-venue" v-if="theatre && theatre.name">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                <circle cx="12" cy="10" r="3"></circle>
              </svg>
              {{ theatre.name }} - {{ theatre.place }}
            </p>
            <p class="show-time">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12 6 12 12 16 14"></polyline>
              </svg>
              {{ formatTime(show.start_time) }} - {{ formatTime(show.end_time) }}
            </p>
            <p class="show-price">
              <span class="price-label">Ticket Price:</span>
              <span class="price-value">₹{{ show.ticket_price }}</span>
            </p>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="!show && !errorMessage" class="loading-state">
          <p>Loading show details...</p>
        </div>

        <!-- Booking Steps -->
        <div class="booking-steps" v-if="show">
          <!-- Step 0: Theatre Selection (if multiple available) -->
          <div class="step-card" :class="{ active: currentStep === 0, completed: currentStep > 0 }" v-if="showTheatreStep">
            <div class="step-header">
              <div class="step-number">1</div>
              <h3>Select Theatre</h3>
            </div>
            <div class="step-content" v-if="currentStep === 0">
              <div class="theatre-list">
                <div 
                  v-for="t in availableTheatres" 
                  :key="t.id"
                  class="theatre-option"
                  :class="{ selected: selectedTheatreId === t.id }"
                  @click="selectTheatre(t)"
                >
                  <div class="theatre-info">
                    <h4>{{ t.name }}</h4>
                    <p class="theatre-place">📍 {{ t.place }}</p>
                    <p class="theatre-capacity">🪑 {{ t.capacity }} seats</p>
                  </div>
                  <div class="theatre-showtimes">
                    <span class="showtime-badge">{{ formatTime(show.start_time) }}</span>
                  </div>
                </div>
              </div>
              <button class="btn-next" @click="confirmTheatre" :disabled="!selectedTheatreId">
                Continue to Date Selection
              </button>
            </div>
            <div class="step-summary" v-else>
              <span>{{ theatre ? theatre.name + ' - ' + theatre.place : 'Select a theatre' }}</span>
              <button class="btn-edit" @click="currentStep = 0">Change</button>
            </div>
          </div>

          <!-- Step 1: Date Selection -->
          <div class="step-card" :class="{ active: currentStep === 1, completed: currentStep > 1 }">
            <div class="step-header">
              <div class="step-number">{{ showTheatreStep ? 2 : 1 }}</div>
              <h3>Select Date</h3>
            </div>
            <div class="step-content" v-if="currentStep === 1">
              <div class="date-picker">
                <div 
                  v-for="date in availableDates" 
                  :key="date.value"
                  class="date-option"
                  :class="{ selected: selectedDate === date.value }"
                  @click="selectDate(date.value)"
                >
                  <span class="date-day">{{ date.day }}</span>
                  <span class="date-num">{{ date.num }}</span>
                  <span class="date-month">{{ date.month }}</span>
                </div>
              </div>
              <button class="btn-next" @click="nextStep" :disabled="!selectedDate">
                Continue to Seat Selection
              </button>
            </div>
            <div class="step-summary" v-else-if="currentStep > 1">
              <span>{{ formatSelectedDate }}</span>
              <button class="btn-edit" @click="currentStep = 1">Change</button>
            </div>
          </div>

          <!-- Step 2: Seat Selection -->
          <div class="step-card" :class="{ active: currentStep === 2, completed: currentStep > 2, disabled: currentStep < 2 }">
            <div class="step-header">
              <div class="step-number">{{ showTheatreStep ? 3 : 2 }}</div>
              <h3>Select Seats</h3>
            </div>
            <div class="step-content" v-if="currentStep === 2">
              <!-- Screen -->
              <div class="screen-container">
                <div class="screen"></div>
                <span class="screen-label">SCREEN</span>
              </div>

              <!-- Seat Map -->
              <div class="seat-map">
                <div v-for="(row, rowIndex) in seatMap" :key="'row-' + rowIndex" class="seat-row">
                  <span class="row-label">{{ row.label }}</span>
                  <div class="seats">
                    <div 
                      v-for="(seat, seatIndex) in row.seats" 
                      :key="'seat-' + rowIndex + '-' + seatIndex"
                      class="seat"
                      :class="{ 
                        selected: isSeatSelected(row.label, seatIndex + 1),
                        booked: seat.booked,
                        held: seat.held && !seat.booked,
                        aisle: seat.aisle
                      }"
                      @click="toggleSeat(row.label, seatIndex + 1, seat)"
                    >
                      <span v-if="!seat.aisle">{{ seatIndex + 1 }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Seat Legend -->
              <div class="seat-legend">
                <div class="legend-item">
                  <div class="seat-sample available"></div>
                  <span>Available</span>
                </div>
                <div class="legend-item">
                  <div class="seat-sample selected"></div>
                  <span>Selected</span>
                </div>
                <div class="legend-item">
                  <div class="seat-sample held"></div>
                  <span>Held</span>
                </div>
                <div class="legend-item">
                  <div class="seat-sample booked"></div>
                  <span>Booked</span>
                </div>
              </div>

              <div class="selection-summary" v-if="selectedSeats.length > 0">
                <p><strong>{{ selectedSeats.length }}</strong> seat(s) selected: {{ selectedSeatsDisplay }}</p>
                <p class="subtotal">Subtotal: <strong>₹{{ subtotal }}</strong></p>
              </div>

              <button class="btn-next" @click="nextStep" :disabled="selectedSeats.length === 0">
                Continue to Payment
              </button>
            </div>
            <div class="step-summary" v-else-if="currentStep > 2">
              <span>{{ selectedSeats.length }} seats - {{ selectedSeatsDisplay }}</span>
              <button class="btn-edit" @click="currentStep = 2">Change</button>
            </div>
          </div>

          <!-- Step 3: Confirm & Pay -->
          <div class="step-card" :class="{ active: currentStep === 3, disabled: currentStep < 3 }">
            <div class="step-header">
              <div class="step-number">{{ showTheatreStep ? 4 : 3 }}</div>
              <h3>Confirm & Pay</h3>
            </div>
            <div class="step-content" v-if="currentStep === 3">
              <div class="booking-summary">
                <div class="summary-row">
                  <span>Show</span>
                  <span>{{ show.name }}</span>
                </div>
                <div class="summary-row">
                  <span>Venue</span>
                  <span>{{ theatre ? theatre.name + ' - ' + theatre.place : 'N/A' }}</span>
                </div>
                <div class="summary-row">
                  <span>Date</span>
                  <span>{{ formatSelectedDate }}</span>
                </div>
                <div class="summary-row">
                  <span>Time</span>
                  <span>{{ formatTime(show.start_time) }}</span>
                </div>
                <div class="summary-row">
                  <span>Seats</span>
                  <span>{{ selectedSeatsDisplay }}</span>
                </div>
                <div class="summary-row">
                  <span>Tickets</span>
                  <span>{{ selectedSeats.length }} × ₹{{ show.ticket_price }}</span>
                </div>
                <div class="summary-divider"></div>
                <div class="summary-row total">
                  <span>Total Amount</span>
                  <span>₹{{ subtotal }}</span>
                </div>
              </div>

              <button class="btn-confirm" @click="confirmBooking" :disabled="isBooking">
                <span v-if="isBooking">Processing...</span>
                <span v-else>Confirm Booking</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Success Modal -->
        <div v-if="bookingSuccess" class="modal-overlay">
          <div class="success-modal">
            <div class="success-icon">✓</div>
            <h2>Booking Confirmed!</h2>
            <p>Your tickets have been booked successfully.</p>
            <div class="ticket-info">
              <p><strong>{{ show.name }}</strong></p>
              <p>{{ formatSelectedDate }} at {{ formatTime(show.start_time) }}</p>
              <p>Seats: {{ selectedSeatsDisplay }}</p>
            </div>
            <button class="btn-primary" @click="goToDashboard">Go to Dashboard</button>
          </div>
        </div>

        <!-- Error Message -->
        <div v-if="errorMessage" class="error-banner">
          {{ errorMessage }}
          <button @click="errorMessage = ''">&times;</button>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import axios from 'axios';
import { io } from 'socket.io-client';
import AppHeader from './AppHeader.vue';

export default {
  name: 'BookingPage',
  components: { AppHeader },
  data() {
    return {
      socket: null,
      show: null,
      theatre: null,
      availableTheatres: [],
      selectedTheatreId: null,
      showTheatreStep: false,
      currentStep: 1,
      selectedDate: null,
      selectedSeats: [],
      seatMap: [],
      isBooking: false,
      bookingSuccess: false,
      errorMessage: '',
      reservationId: null,
      holdTTL: 120,
      placeholder: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='450' viewBox='0 0 300 450'%3E%3Crect fill='%23374151' width='300' height='450'/%3E%3Ctext fill='%239ca3af' font-family='sans-serif' font-size='16' x='50%25' y='50%25' text-anchor='middle' dy='.3em'%3ENo Image%3C/text%3E%3C/svg%3E"
    };
  },
  computed: {
    availableDates() {
      const dates = [];
      const today = new Date();
      for (let i = 0; i < 7; i++) {
        const date = new Date(today);
        date.setDate(today.getDate() + i);
        dates.push({
          value: date.toISOString().split('T')[0],
          day: date.toLocaleDateString('en-US', { weekday: 'short' }),
          num: date.getDate(),
          month: date.toLocaleDateString('en-US', { month: 'short' })
        });
      }
      return dates;
    },
    formatSelectedDate() {
      if (!this.selectedDate) return '';
      const date = new Date(this.selectedDate);
      return date.toLocaleDateString('en-US', { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      });
    },
    selectedSeatsDisplay() {
      return this.selectedSeats.map(s => `${s.row}${s.num}`).join(', ');
    },
    subtotal() {
      if (!this.show || !this.show.ticket_price) return 0;
      return this.selectedSeats.length * this.show.ticket_price;
    }
  },
  created() {
    this.loadShowDetails();
    this.generateSeatMap();
  },
  beforeUnmount() {
    if (this.socket) {
      try {
        if (this.show && this.show.id) this.socket.emit('leave', { show_id: this.show.id });
        this.socket.disconnect();
      } catch (e) {
        // ignore
      }
    }
  },
  watch: {
    // initialize socket once show data is available
    show(newVal) {
      if (newVal) this.initSocket();
    }
  },
  methods: {
    async loadShowDetails() {
      const showId = this.$route.params.id;
      if (!showId) {
        this.errorMessage = 'No show selected';
        return;
      }

      try {
        const token = localStorage.getItem('access_token');
        const headers = token ? { Authorization: `Bearer ${token}` } : {};
        
        // Prefer querying the local DB first (most routes use DB id).
        // If that fails, fall back to TMDB lookup so TMDB-based IDs still work.
        const dbResp = await axios.get(`shows/${showId}`, {
          headers,
          validateStatus: (status) => status >= 200 && status < 500,
        });

        if (dbResp.status === 200) {
          this.show = dbResp.data;
        } else {
          // DB lookup returned not-found; try TMDB lookup as a fallback.
          const tmdbResp = await axios.get(`shows/tmdb/${showId}`, {
            headers,
            validateStatus: (status) => status >= 200 && status < 500,
          });
          if (tmdbResp.status === 200) {
            this.show = tmdbResp.data;
          } else {
            // Neither DB nor TMDB returned a show
            throw new Error('Show not found');
          }
        }
        console.log('Loaded show:', this.show);
        console.log('Ticket price:', this.show.ticket_price);
        
        // Load all theatres to potentially show options
        const theatresRes = await axios.get('theatres', { headers });
        this.availableTheatres = theatresRes.data;
        
        // If show has a specific theatre, load it
        if (this.show.theatre_id) {
          const theatreRes = await axios.get(`theatres/${this.show.theatre_id}`, { headers });
          this.theatre = theatreRes.data;
          this.selectedTheatreId = this.theatre.id;
          this.generateSeatMap(this.theatre.capacity);
          
          // If multiple theatres available, show theatre selection step
          if (this.availableTheatres.length > 1) {
            this.showTheatreStep = true;
            this.currentStep = 0;
          }
        } else if (this.availableTheatres.length > 0) {
          // No theatre assigned to show, let user select from available theatres
          this.showTheatreStep = true;
          this.currentStep = 0;
          // Pre-select the first theatre
          this.selectTheatre(this.availableTheatres[0]);
        }
      } catch (error) {
        console.error('Error loading show:', error);
        this.errorMessage = 'Failed to load show details';
      }
    },
    selectTheatre(theatre) {
      this.selectedTheatreId = theatre.id;
      this.theatre = theatre;
    },
    confirmTheatre() {
      if (this.selectedTheatreId) {
        this.generateSeatMap(this.theatre.capacity);
        this.currentStep = 1;
      }
    },
    truncateText(text, length) {
      if (!text) return '';
      return text.length > length ? text.substring(0, length) + '...' : text;
    },
    async generateSeatMap() {
      if (!this.theatre) return;
      
      try {
        // Fetch all seats for this theatre
        const seatsResponse = await axios.get(`theatres/${this.theatre.id}/seats`);
        const theatreSeats = seatsResponse.data.seats;
        
        // Fetch booked seats and active holds for this show
        const bookedResponse = await axios.get(`shows/${this.show.id}/booked-seats`);
        const bookedSeatIds = bookedResponse.data.booked_seats || [];
        const heldMap = bookedResponse.data.held_seats_map || {};
        
        // Group seats by row
        const seatsByRow = {};
        theatreSeats.forEach(seat => {
          if (!seatsByRow[seat.row_label]) {
            seatsByRow[seat.row_label] = [];
          }
          const seatKey = `${seat.row_label}${seat.seat_number}`;
          // heldMap keys may be stored as seat ids or row+number depending on backend mapping; check both
          const heldReservation = heldMap[seat.seat_id] || heldMap[seatKey] || null;
          seatsByRow[seat.row_label].push({
            number: seat.seat_number,
            booked: bookedSeatIds.includes(seat.seat_id),
            held: heldReservation !== null,
            heldReservationId: heldReservation,
            type: seat.seat_type,
            active: seat.is_active
          });
        });
        
        // Sort seats within each row by number
        Object.keys(seatsByRow).forEach(row => {
          seatsByRow[row].sort((a, b) => a.number - b.number);
        });
        
        // Convert to seat map format
        this.seatMap = Object.keys(seatsByRow)
          .sort() // Sort rows alphabetically
          .map(rowLabel => ({
            label: rowLabel,
            seats: seatsByRow[rowLabel].map(seat => ({
              number: seat.number,
              seat_id: `${rowLabel}${seat.number}`,
              booked: seat.booked,
              aisle: false, // We'll handle aisles differently now
              type: seat.type,
              active: seat.active,
              held: seat.held || false,
              heldReservationId: seat.heldReservationId || null
            }))
          }));
          
      } catch (error) {
        console.error('Error loading seat map:', error);
        // Fallback to old method if API fails
        this.generateSeatMapFallback();
      }
    },
    initSocket() {
      try {
        const backendUrl = axios.defaults.baseURL || '';
        this.socket = io(backendUrl, { transports: ['websocket', 'polling'] });

        this.socket.on('connect', () => {
          if (this.show && this.show.id) {
            this.socket.emit('join', { show_id: this.show.id });
          }
        });

        this.socket.on('seat_update', (data) => {
          try {
            console.debug('seat_update event received', data);
            if (!data) return;
            if (String(data.show_id) !== String(this.show?.id)) return;

            const type = data.type;
            const payload = data.data || {};

            // Handle per-seat updates locally when possible to avoid full reload
            if (type === 'seat_held' || type === 'seat_released' || type === 'seat_confirmed') {
              const seats = payload.seats || [];
              const resId = payload.reservation_id ? String(payload.reservation_id) : null;

              seats.forEach(seatId => {
                // seatId is like 'B12'
                const row = seatId.replace(/\d+$/, '');
                const numMatch = seatId.match(/(\d+)$/);
                const num = numMatch ? parseInt(numMatch[1], 10) : null;
                if (!row || !num) return;

                const rowObj = this.seatMap.find(r => r.label === row);
                if (!rowObj) return;
                // Find seat by seat_id or by number (safer than assuming array index)
                const seatObj = rowObj.seats.find(s => s.seat_id === seatId || s.number === num);
                if (!seatObj) return;

                if (type === 'seat_held') {
                  seatObj.held = true;
                  seatObj.heldReservationId = resId;
                } else if (type === 'seat_released') {
                  seatObj.held = false;
                  seatObj.heldReservationId = null;
                } else if (type === 'seat_confirmed') {
                  // confirmed means booked
                  seatObj.held = false;
                  seatObj.heldReservationId = null;
                  seatObj.booked = true;
                }
              });

              return;
            }

            // Fallback: refresh seat map
            this.generateSeatMap();
          } catch (e) {
            console.error('Error handling seat_update:', e);
            // fallback to refresh
            try { this.generateSeatMap(); } catch (_) { }
          }
        });

        this.socket.on('disconnect', () => {
          // no-op for now
        });
      } catch (e) {
        console.error('Socket init error:', e);
      }
    },
    generateSeatMapFallback(capacity = 100) {
      // Fallback method for when API fails
      const rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'];
      const seatsPerRow = Math.ceil(capacity / rows.length);
      
      this.seatMap = rows.map(label => ({
        label,
        seats: Array.from({ length: seatsPerRow }, (_, i) => ({
          booked: Math.random() < 0.2,
          aisle: i === Math.floor(seatsPerRow / 2) - 1,
          type: 'regular',
          active: true
        }))
      }));
    },
    selectDate(date) {
      this.selectedDate = date;
    },
    isSeatSelected(row, num) {
      return this.selectedSeats.some(s => s.row === row && s.num === num);
    },
    toggleSeat(row, num, seat) {
      // Prevent selecting permanently booked seats or inactive seats
      if (seat.booked || !seat.active) return;
      // Prevent selecting seats held by other users
      if (seat.held && seat.heldReservationId && String(seat.heldReservationId) !== String(this.reservationId)) return;
      
      const index = this.selectedSeats.findIndex(s => s.row === row && s.num === num);
      if (index > -1) {
        this.selectedSeats.splice(index, 1);
      } else {
        this.selectedSeats.push({ row, num });
      }
    },
    async nextStep() {
      // When moving from seat selection (step 2) to payment (step 3), create a seat hold
      try {
        if (this.currentStep === 2) {
          // Attempt to hold selected seats before advancing
          try {
            await this.holdSelectedSeats();
          } catch (e) {
            console.error('Failed to hold seats:', e);
            this.errorMessage = e.message || 'Failed to hold seats. Please try again.';
            return;
          }
        }

        if (this.currentStep < 3) {
          this.currentStep++;
        }
      } catch (e) {
        console.error('nextStep error', e);
        this.errorMessage = 'Unable to proceed';
      }
    },
    async confirmBooking() {
      const token = localStorage.getItem('access_token');
      if (!token) {
        this.$router.push('/login');
        return;
      }

      this.isBooking = true;
      this.errorMessage = '';

      try {
        const response = await axios.post(
          `bookshows/${this.show.id}/book`,
          { 
            seats: this.selectedSeats,  // Send array of {row, num} objects
            date: this.selectedDate,
            reservation_id: this.reservationId
          },
          { headers: { Authorization: `Bearer ${token}` } }
        );

        if (response.data) {
          this.bookingSuccess = true;
        }
      } catch (error) {
        console.error('Booking error:', error);
        this.errorMessage = error.response?.data?.message || 'Booking failed. Please try again.';
        // Release reservation on failure so seats free up
        try { await this.releaseSeatHold(); } catch (e) { /* ignore */ }
      } finally {
        this.isBooking = false;
      }
    },
    async holdSelectedSeats() {
      if (!this.selectedSeats || this.selectedSeats.length === 0) {
        throw new Error('No seats selected to hold');
      }
      const token = localStorage.getItem('access_token');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      const seatIds = this.selectedSeats.map(s => `${s.row}${s.num}`);
      const resp = await axios.post(
        `shows/${this.show.id}/hold`,
        { seats: seatIds, ttl_seconds: this.holdTTL },
        { headers, validateStatus: s => s < 500 }
      );

      // Success: 201
      if (resp.status === 201) {
        this.reservationId = resp.data.reservation_id;
        // Mark these seats locally as held to immediately reflect in UI
        try {
          const resId = String(this.reservationId);
          this.selectedSeats.forEach(sel => {
            const seatId = `${sel.row}${sel.num}`;
            const rowObj = this.seatMap.find(r => r.label === sel.row);
            if (!rowObj) return;
            const seatObj = rowObj.seats.find(s => s.seat_id === seatId || s.number === sel.num);
            if (seatObj) {
              seatObj.held = true;
              seatObj.heldReservationId = resId;
            }
          });
        } catch (e) {
          // ignore UI marking errors
        }
        return resp.data;
      }

      // Conflict: seat already held - backend returns 'SEAT_ALREADY_HELD:<seatId>'
      if (resp.status === 409) {
        const msg = resp.data?.message || '';
        // Parse seat id from message if present
        if (typeof msg === 'string' && msg.startsWith('SEAT_ALREADY_HELD')) {
          const parts = msg.split(':');
          const seatId = parts.length > 1 ? parts[1] : null;
          if (seatId) {
            try {
              // Mark the specific seat as held in the UI so user can see it
              const row = seatId.replace(/\d+$/, '');
              const numMatch = seatId.match(/(\d+)$/);
              const num = numMatch ? parseInt(numMatch[1], 10) : null;
              const rowObj = this.seatMap.find(r => r.label === row);
              if (rowObj) {
                const seatObj = rowObj.seats.find(s => s.seat_id === seatId || s.number === num);
                if (seatObj) {
                  seatObj.held = true;
                  seatObj.heldReservationId = 'other';
                }
              }
            } catch (e) {
              // ignore UI marking errors
            }
          }
        }
        // Bubble a helpful message so caller (nextStep) can stop progression
        throw new Error(resp.data?.message || 'Seat already held by another user');
      }

      throw new Error(resp.data?.message || 'Failed to hold seats');
    },
    async releaseSeatHold() {
      if (!this.reservationId) return;
      const token = localStorage.getItem('access_token');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      try {
        await axios.delete(`shows/${this.show.id}/hold/${this.reservationId}`, { headers });
      } catch (e) {
        // ignore errors
      } finally {
        this.reservationId = null;
      }
    },
    formatTime(datetime) {
      if (!datetime) return '';
      const date = new Date(datetime);
      return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    },
    handleImageError(e) {
      e.target.src = this.placeholder;
    },
    goBack() {
      // Release any active seat hold before navigating back
      try {
        this.releaseSeatHold();
      } catch (e) {
        // ignore
      }
      this.$router.go(-1);
    },
    goToProfile() {
      const token = localStorage.getItem('access_token');
      if (token) {
        this.$router.push('/userprofile');
      } else {
        this.$router.push('/login');
      }
    },
    goToDashboard() {
      this.$router.push('/userdashboard');
    }
  }
};
</script>

<style scoped>
.booking-page {
  min-height: 100vh;
  background:
    radial-gradient(circle at 0% 0%, rgba(217, 212, 241, 0.9) 0, transparent 55%),
    radial-gradient(circle at 100% 0%, rgba(250, 220, 217, 0.9) 0, transparent 55%),
    radial-gradient(circle at 0% 100%, rgba(215, 234, 248, 0.9) 0, transparent 55%),
    #f9fafb;
}

.container {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 20px;
}

.page-header {
  padding: 20px 0;
}

.page-header .container {
  display: flex;
  align-items: center;
  gap: 20px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, #a855f7 0%, #ec4899 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
}

.btn-back {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: transparent;
  border: 1px solid rgba(168, 85, 247, 0.2);
  border-radius: 10px;
  color: #6b7280;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-back:hover {
  border-color: #a855f7;
  color: #a855f7;
}

.booking-main {
  padding: 30px 0 60px;
}

/* Show Info Card */
.show-info-card {
  display: flex;
  gap: 24px;
  padding: 24px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  border: 1px solid rgba(168, 85, 247, 0.1);
  margin-bottom: 30px;
}

.show-poster {
  width: 140px;
  flex-shrink: 0;
}

.show-poster img {
  width: 100%;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.show-details {
  flex: 1;
}

.show-title {
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 12px;
  color: #0f172a;
}

.show-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0 0 12px;
}

.tag {
  padding: 4px 12px;
  background: rgba(168, 85, 247, 0.1);
  color: #a855f7;
  font-size: 12px;
  font-weight: 600;
  border-radius: 20px;
}

.rating {
  color: #f59e0b;
  font-weight: 600;
}

.runtime {
  color: #6b7280;
  font-size: 12px;
}

.show-overview {
  color: #6b7280;
  font-size: 13px;
  line-height: 1.5;
  margin: 0 0 12px;
}

.show-venue, .show-time {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #6b7280;
  font-size: 14px;
  margin: 0 0 8px;
}

.show-price {
  margin-top: 16px;
}

.price-label {
  color: #6b7280;
  font-size: 14px;
}

.price-value {
  font-size: 24px;
  font-weight: 700;
  color: #a855f7;
  margin-left: 8px;
}

/* Steps */
.booking-steps {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.step-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  border: 1px solid rgba(168, 85, 247, 0.1);
  overflow: hidden;
  transition: all 0.3s;
}

.step-card.active {
  border-color: #a855f7;
  box-shadow: 0 4px 20px rgba(168, 85, 247, 0.15);
}

.step-card.disabled {
  opacity: 0.5;
  pointer-events: none;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 24px;
  border-bottom: 1px solid rgba(168, 85, 247, 0.05);
}

.step-number {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #a855f7 0%, #ec4899 100%);
  color: white;
  font-weight: 700;
  border-radius: 50%;
  font-size: 14px;
}

.step-card.completed .step-number {
  background: #22c55e;
}

.step-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #0f172a;
}

.step-content {
  padding: 24px;
}

.step-summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background: rgba(168, 85, 247, 0.03);
  color: #6b7280;
}

.btn-edit {
  padding: 6px 14px;
  background: transparent;
  border: 1px solid rgba(168, 85, 247, 0.3);
  border-radius: 8px;
  color: #a855f7;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
}

/* Theatre Selection */
.theatre-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.theatre-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: rgba(168, 85, 247, 0.05);
  border: 2px solid transparent;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.theatre-option:hover {
  border-color: rgba(168, 85, 247, 0.3);
  background: rgba(168, 85, 247, 0.08);
}

.theatre-option.selected {
  border-color: #a855f7;
  background: rgba(168, 85, 247, 0.1);
}

.theatre-info h4 {
  margin: 0 0 6px;
  font-size: 16px;
  font-weight: 600;
  color: #0f172a;
}

.theatre-place {
  margin: 0 0 4px;
  font-size: 13px;
  color: #6b7280;
}

.theatre-capacity {
  margin: 0;
  font-size: 12px;
  color: #9ca3af;
}

.theatre-showtimes {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.showtime-badge {
  padding: 6px 12px;
  background: linear-gradient(135deg, #a855f7 0%, #ec4899 100%);
  color: white;
  font-size: 13px;
  font-weight: 600;
  border-radius: 8px;
}

/* Date Picker */
.date-picker {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  padding-bottom: 16px;
  margin-bottom: 20px;
}

.date-option {
  min-width: 70px;
  padding: 16px 12px;
  background: rgba(168, 85, 247, 0.05);
  border: 2px solid transparent;
  border-radius: 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}

.date-option:hover {
  border-color: rgba(168, 85, 247, 0.3);
}

.date-option.selected {
  background: linear-gradient(135deg, #a855f7 0%, #ec4899 100%);
  color: white;
}

.date-day {
  display: block;
  font-size: 12px;
  font-weight: 500;
  opacity: 0.7;
}

.date-num {
  display: block;
  font-size: 24px;
  font-weight: 700;
  margin: 4px 0;
}

.date-month {
  display: block;
  font-size: 12px;
  opacity: 0.7;
}

/* Screen */
.screen-container {
  text-align: center;
  margin-bottom: 30px;
}

.screen {
  width: 80%;
  height: 8px;
  margin: 0 auto 8px;
  background: linear-gradient(135deg, #a855f7 0%, #ec4899 100%);
  border-radius: 50%;
  box-shadow: 0 0 20px rgba(168, 85, 247, 0.4);
}

.screen-label {
  font-size: 11px;
  color: #9ca3af;
  letter-spacing: 2px;
}

/* Seat Map */
.seat-map {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  margin-bottom: 24px;
}

.seat-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.row-label {
  width: 24px;
  font-size: 12px;
  font-weight: 600;
  color: #9ca3af;
  text-align: center;
}

.seats {
  display: flex;
  gap: 6px;
}

.seat {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(168, 85, 247, 0.1);
  border: 2px solid rgba(168, 85, 247, 0.2);
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s;
}

.seat:hover:not(.booked):not(.aisle) {
  border-color: #a855f7;
  transform: scale(1.1);
}

.seat.selected {
  background: linear-gradient(135deg, #a855f7 0%, #ec4899 100%);
  border-color: #a855f7;
  color: white;
}

.seat.held {
  background: linear-gradient(135deg, #f59e0b 0%, #fb923c 100%);
  border-color: #f97316;
  color: white;
  cursor: not-allowed;
}

.seat.booked {
  background: #e5e7eb;
  border-color: #d1d5db;
  color: #9ca3af;
  cursor: not-allowed;
}

.seat.aisle {
  background: transparent;
  border: none;
  cursor: default;
  width: 16px;
}

/* Seat Legend */
.seat-legend {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-bottom: 24px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #6b7280;
}

.seat-sample {
  width: 20px;
  height: 20px;
  border-radius: 4px;
}

.seat-sample.available {
  background: rgba(168, 85, 247, 0.1);
  border: 2px solid rgba(168, 85, 247, 0.2);
}

.seat-sample.held {
  background: linear-gradient(135deg, #f59e0b 0%, #fb923c 100%);
  border: 2px solid #f97316;
}

.seat-sample.selected {
  background: linear-gradient(135deg, #a855f7 0%, #ec4899 100%);
}

.seat-sample.booked {
  background: #e5e7eb;
}

.selection-summary {
  text-align: center;
  padding: 16px;
  background: rgba(168, 85, 247, 0.05);
  border-radius: 12px;
  margin-bottom: 20px;
}

.selection-summary p {
  margin: 0 0 4px;
  color: #6b7280;
}

.subtotal {
  font-size: 18px;
  color: #0f172a;
}

/* Buttons */
.btn-next, .btn-confirm {
  width: 100%;
  padding: 16px;
  background: linear-gradient(135deg, #a855f7 0%, #ec4899 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-next:hover:not(:disabled), .btn-confirm:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(168, 85, 247, 0.3);
}

.btn-next:disabled, .btn-confirm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Booking Summary */
.booking-summary {
  margin-bottom: 24px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid rgba(168, 85, 247, 0.05);
  font-size: 14px;
}

.summary-row span:first-child {
  color: #6b7280;
}

.summary-row span:last-child {
  font-weight: 500;
  color: #0f172a;
}

.summary-divider {
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(168, 85, 247, 0.2), transparent);
  margin: 8px 0;
}

.summary-row.total {
  border-bottom: none;
  font-size: 18px;
}

.summary-row.total span:last-child {
  font-weight: 700;
  color: #a855f7;
}

/* Success Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  backdrop-filter: blur(4px);
}

.success-modal {
  background: white;
  border-radius: 24px;
  padding: 40px;
  text-align: center;
  max-width: 400px;
  margin: 20px;
}

.success-icon {
  width: 72px;
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
  color: white;
  font-size: 36px;
  border-radius: 50%;
  margin: 0 auto 20px;
}

.success-modal h2 {
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 8px;
  color: #0f172a;
}

.success-modal > p {
  color: #6b7280;
  margin: 0 0 24px;
}

.ticket-info {
  background: rgba(168, 85, 247, 0.05);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 24px;
}

.ticket-info p {
  margin: 0 0 4px;
  color: #6b7280;
}

.ticket-info p:first-child {
  color: #0f172a;
  font-size: 16px;
}

.btn-primary {
  padding: 14px 32px;
  background: linear-gradient(135deg, #a855f7 0%, #ec4899 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
}

/* Loading State */
.loading-state {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 60px 20px;
  color: #6b7280;
  font-size: 16px;
}

/* Error Banner */
.error-banner {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 12px;
  color: #dc2626;
  font-size: 14px;
  z-index: 50;
}

.error-banner button {
  background: none;
  border: none;
  font-size: 18px;
  color: #dc2626;
  cursor: pointer;
}

/* Responsive */
@media (max-width: 640px) {
  .show-info-card {
    flex-direction: column;
    text-align: center;
  }
  
  .show-poster {
    width: 120px;
    margin: 0 auto;
  }
  
  .show-venue, .show-time {
    justify-content: center;
  }
  
  .seat {
    width: 28px;
    height: 28px;
    font-size: 10px;
  }
}
</style>
