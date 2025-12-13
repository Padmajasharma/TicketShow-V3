<template>
  <div class="admin-dashboard">
    <AppHeader @toggle-search="() => {}" @go-profile="() => {}" />
    
    <!-- Page Title Section -->
    <div class="page-header">
      <div class="container">
        <div class="header-left">
          <h1 class="page-title">Admin Dashboard</h1>
          <p class="page-subtitle">Manage theatres, shows, and view analytics</p>
        </div>
      </div>
    </div>

    <main class="admin-main">
      <div class="container">
        <div v-if="message" class="message-banner">{{ message }}</div>

        <div class="quick-actions">
          <router-link to="/theatres" class="action-card">
            <div class="action-icon">🎭</div>
            <div class="action-content">
              <h3>Manage Theatres</h3>
              <p>Add, edit or remove venues</p>
            </div>
            <svg class="action-arrow" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="m9 18 6-6-6-6"></path>
            </svg>
          </router-link>

          <router-link to="/shows" class="action-card">
            <div class="action-icon">🎬</div>
            <div class="action-content">
              <h3>Manage Shows</h3>
              <p>Schedule and update shows</p>
            </div>
            <svg class="action-arrow" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="m9 18 6-6-6-6"></path>
            </svg>
          </router-link>
          
          <div @click="navigateToAnalytics" @keydown.enter="navigateToAnalytics" role="button" tabindex="0" class="action-card">
            <div class="action-icon">📊</div>
            <div class="action-content">
              <h3>View Analytics</h3>
              <p>Sales, revenue and performance by show or city</p>
            </div>
            <svg class="action-arrow" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="m9 18 6-6-6-6"></path>
            </svg>
          </div>
        </div>

        <div v-if="imgUrl" class="chart-section">
          <div class="section-header">
            <h2>Popularity Analytics</h2>
            <p>Show performance overview</p>
          </div>
          <div class="chart-card">
            <img :src="imgUrl" alt="Popularity Graph" class="chart-img" />
          </div>
        </div>
        <!-- analytics is available on its own page at /admin/analytics -->
      </div>
    </main>
  </div>
</template>

<script>
import { jwtDecode } from "jwt-decode";
import axios from "axios";
import AppHeader from './AppHeader.vue';

export default {
  components: { AppHeader },
  data() {
    return {
      message: "",
      imgUrl: "",
      // no embedded analytics; navigate to dedicated analytics page
    };
  },
  created() {
    const token = localStorage.getItem("access_token");
    if (token) {
      const decodedToken = jwtDecode(token);
      const expirationTime = decodedToken.exp * 1000;
      const currentTime = Date.now();

      const timeUntilExpiration = expirationTime - currentTime;
      setTimeout(() => {
        this.logout();
      }, timeUntilExpiration);
    }
    this.fetchImage();
  },
  methods: {
    logout() {
      localStorage.removeItem("access_token");
      this.$router.push("/");
    },
    navigateToAnalytics() {
      // Use path navigation to avoid named-route resolution errors
      // Force a full-page navigation to ensure the latest router bundle is loaded
      try {
        window.location.href = '/admin/analytics';
      } catch (e) {
        this.$router.push('/admin/analytics').catch(() => {});
      }
    },
    fetchImage() {
      axios.get("popularity_graph_image")
        .then((response) => {
          console.log(response.data);
          this.imgUrl = response.data;
        })
        .catch((error) => {
          console.error("Error fetching image:", error);
        });
    }
  },
};
</script>

<style scoped>
.admin-dashboard {
  min-height: 100vh;
  background:
    radial-gradient(circle at 0% 0%, rgba(217, 212, 241, 0.9) 0, transparent 55%),
    radial-gradient(circle at 100% 0%, rgba(250, 220, 217, 0.9) 0, transparent 55%),
    radial-gradient(circle at 0% 100%, rgba(215, 234, 248, 0.9) 0, transparent 55%),
    #f9fafb;
}

.container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 20px;
}

.page-header {
  padding: 30px 0 20px;
}

.page-header .container {
  display: flex;
  align-items: center;
  justify-content: space-between;
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

.logout-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.logout-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3);
}

.admin-main {
  padding: 40px 0;
}

.message-banner {
  padding: 14px 20px;
  background: rgba(168, 85, 247, 0.1);
  border: 1px solid rgba(168, 85, 247, 0.2);
  border-radius: 12px;
  color: #a855f7;
  font-weight: 500;
  margin-bottom: 30px;
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.action-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px;
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(168, 85, 247, 0.1);
  border-radius: 16px;
  text-decoration: none;
  color: inherit;
  transition: all 0.2s ease;
}

.action-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 30px rgba(168, 85, 247, 0.12);
  border-color: rgba(168, 85, 247, 0.2);
}

/* Make action cards appear clickable */
.action-card { cursor: pointer; }

.action-icon {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(168, 85, 247, 0.1) 0%, rgba(236, 72, 153, 0.1) 100%);
  border-radius: 14px;
  font-size: 24px;
}

.action-content {
  flex: 1;
}

.action-content h3 {
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 4px;
  color: #0f172a;
}

.action-content p {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}

.action-arrow {
  color: #a855f7;
}

.chart-section {
  margin-top: 40px;
}

.section-header {
  margin-bottom: 20px;
}

.section-header h2 {
  font-size: 22px;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 4px;
}

.section-header p {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}

.chart-card {
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(168, 85, 247, 0.1);
  border-radius: 16px;
  padding: 24px;
  overflow: hidden;
}

.chart-img {
  width: 100%;
  height: auto;
  border-radius: 8px;
}
</style>
