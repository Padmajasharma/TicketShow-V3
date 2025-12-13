<template>
  <div class="profile-page">
    <AppHeader @toggle-search="() => {}" @go-profile="() => {}" />
    
    <!-- Page Title Section -->
    <div class="page-header">
      <div class="container">
        <h1 class="page-title">My Profile</h1>
        <p class="page-subtitle">View your account details and booking history</p>
      </div>
    </div>

    <main class="profile-main">
      <div class="container">
        <div class="profile-grid">
          <!-- User Details Card -->
          <div class="card user-card">
            <div class="card-header">
              <div class="avatar">{{ user.username ? user.username.charAt(0).toUpperCase() : '?' }}</div>
              <div class="user-info">
                <h2>{{ user.username || 'User' }}</h2>
                <p>{{ user.email || 'No email' }}</p>
              </div>
            </div>
            <div class="card-body">
              <div class="info-row">
                <span class="info-label">Username</span>
                <span class="info-value">{{ user.username }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Email</span>
                <span class="info-value">{{ user.email }}</span>
              </div>
            </div>
          </div>

          <!-- Booking History Card -->
          <div class="card bookings-card">
            <div class="section-header">
              <h2>Booking History</h2>
              <span class="badge">{{ bookedTickets.length }} bookings</span>
            </div>
            
            <div v-if="bookedTickets.length === 0" class="empty-state">
              <p>No bookings yet. Start exploring shows!</p>
            </div>
            
            <div v-else class="bookings-list">
              <div v-for="ticket in bookedTickets" :key="ticket.show_name" class="booking-item">
                <div class="booking-main">
                  <h3>{{ ticket.show_name }}</h3>
                  <div class="booking-meta">
                    <span>{{ ticket.show_start_time }} - {{ ticket.show_end_time }}</span>
                  </div>
                </div>
                <div class="booking-tickets">
                  <span class="ticket-count">{{ ticket.ticket_count }}</span>
                  <span class="ticket-label">tickets</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import axios from 'axios';
import AppHeader from './AppHeader.vue';

export default {
  components: { AppHeader },
  data() {
    return {
      user: {},
      bookedTickets: []
    };
  },
  mounted() {
    this.fetchUserData();
  },
  methods: {
    logout() {
      localStorage.removeItem('access_token');
      this.$router.push('/');
    },
    goToDashboard() {
      this.$router.push('/userdashboard');
    },
    async fetchUserData() {
      const token = localStorage.getItem('access_token');
      if (!token) {
        console.error('Unauthorized: JWT token not found');
        this.$router.push('/login');
        return;
      }

      const headers = {
        Authorization: `Bearer ${token}`,
      };

      try {
        const response = await axios.get('userprofile', { headers });
        this.user = response.data.user;
        this.bookedTickets = response.data.booked_shows;
      } catch (error) {
        console.error('Error fetching user data:', error);
      }
    }
  }
};
</script>

<style scoped>
.profile-page {
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
  padding: 30px 0 20px;
}

.page-title {
  font-size: 28px;
  font-weight: 800;
  background: linear-gradient(135deg, #a855f7 0%, #ec4899 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 4px;
}

.page-subtitle {
  color: #6b7280;
  font-size: 14px;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.btn-dashboard, .btn-logout {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-dashboard {
  background: linear-gradient(135deg, #a855f7 0%, #ec4899 100%);
  color: white;
}

.btn-dashboard:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(168, 85, 247, 0.3);
}

.btn-logout {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.btn-logout:hover {
  background: #ef4444;
  color: white;
}

.profile-main {
  padding: 40px 0;
}

.profile-grid {
  display: grid;
  gap: 24px;
}

.card {
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(168, 85, 247, 0.1);
  border-radius: 20px;
  padding: 28px;
}

.user-card .card-header {
  display: flex;
  align-items: center;
  gap: 20px;
  padding-bottom: 24px;
  border-bottom: 1px solid rgba(168, 85, 247, 0.08);
  margin-bottom: 24px;
}

.avatar {
  width: 72px;
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #a855f7 0%, #ec4899 100%);
  color: white;
  font-size: 28px;
  font-weight: 700;
  border-radius: 50%;
}

.user-info h2 {
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 4px;
  color: #0f172a;
}

.user-info p {
  color: #6b7280;
  margin: 0;
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid rgba(168, 85, 247, 0.05);
}

.info-row:last-child {
  border-bottom: none;
}

.info-label {
  color: #6b7280;
  font-size: 14px;
}

.info-value {
  font-weight: 600;
  color: #0f172a;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.section-header h2 {
  font-size: 20px;
  font-weight: 700;
  margin: 0;
  color: #0f172a;
}

.badge {
  padding: 6px 12px;
  background: rgba(168, 85, 247, 0.1);
  color: #a855f7;
  font-size: 12px;
  font-weight: 600;
  border-radius: 20px;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #6b7280;
}

.bookings-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.booking-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: rgba(168, 85, 247, 0.03);
  border: 1px solid rgba(168, 85, 247, 0.08);
  border-radius: 14px;
  transition: all 0.2s ease;
}

.booking-item:hover {
  background: rgba(168, 85, 247, 0.06);
}

.booking-main h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 4px;
  color: #0f172a;
}

.booking-meta {
  font-size: 13px;
  color: #6b7280;
}

.booking-tickets {
  text-align: center;
}

.ticket-count {
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: #a855f7;
}

.ticket-label {
  font-size: 11px;
  color: #6b7280;
  text-transform: uppercase;
}
</style>