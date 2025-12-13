<template>
  <header class="nav-floating">
    <div class="container nav-inner">
      <!-- Left: logo + links -->
      <div class="nav-left">
        <div class="logo-wordmark">
          NovaSeat
        </div>

        <nav class="nav-links">
          <router-link to="/" exact>Home</router-link>
          <router-link to="/movies">Movies</router-link>
          <router-link to="/concerts">Concerts</router-link>
          <router-link to="/plays">Plays</router-link>
          <router-link to="/events">Events</router-link>
        </nav>
      </div>

      <!-- Right: actions -->
      <div class="nav-right">
        <button class="icon-btn" aria-label="search" @click="$emit('toggle-search')">
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="11" cy="11" r="7"></circle>
            <path d="m21 21-4.3-4.3"></path>
          </svg>
        </button>

        <!-- Show Profile & Logout when logged in -->
        <template v-if="isLoggedIn">
          <button class="header-btn dashboard-btn" @click="goToDashboard">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="3" width="7" height="7"></rect>
              <rect x="14" y="3" width="7" height="7"></rect>
              <rect x="14" y="14" width="7" height="7"></rect>
              <rect x="3" y="14" width="7" height="7"></rect>
            </svg>
            Dashboard
          </button>
          <button class="header-btn profile-btn" @click="goToProfile">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>
            Profile
          </button>
          <button class="header-btn logout-btn" @click="logout">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
              <polyline points="16 17 21 12 16 7"></polyline>
              <line x1="21" y1="12" x2="9" y2="12"></line>
            </svg>
            Logout
          </button>
        </template>

        <!-- Show avatar button when not logged in -->
        <button v-else class="avatar-button" aria-label="profile" @click="$emit('go-profile')">
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
            <circle cx="12" cy="7" r="4"></circle>
          </svg>
        </button>
      </div>
    </div>
  </header>
</template>

<script>
import { clearAuthData } from '../utils/auth';

export default {
  name: 'AppHeader',
  data() {
    return {
      isLoggedIn: false
    };
  },
  created() {
    this.checkLoginStatus();
    // Listen for auth expiration events
    window.addEventListener('auth-expired', this.handleAuthExpired);
  },
  beforeUnmount() {
    window.removeEventListener('auth-expired', this.handleAuthExpired);
  },
  methods: {
    checkLoginStatus() {
      this.isLoggedIn = !!localStorage.getItem('access_token');
    },
    handleAuthExpired() {
      this.isLoggedIn = false;
    },
    goToProfile() {
      this.$router.push('/userprofile');
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
      clearAuthData();
      this.isLoggedIn = false;
      this.$router.push('/');
    }
  }
};
</script>

<style scoped>
.nav-floating {
  position: sticky;
  top: 0;
  z-index: 40;
  backdrop-filter: saturate(180%) blur(18px);
  -webkit-backdrop-filter: saturate(180%) blur(18px);
  background:
    radial-gradient(circle at 0% 0%, rgba(129, 140, 248, 0.18), transparent 55%),
    radial-gradient(circle at 100% 0%, rgba(244, 114, 182, 0.16), transparent 55%),
    rgba(255, 255, 255, 0.92);
  border-bottom: 1px solid rgba(209, 213, 219, 0.55);
  box-shadow: 0 14px 40px rgba(15, 23, 42, 0.12);
}

.container {
  max-width: 1180px;
  margin: 0 auto;
  padding: 0 20px;
}

.nav-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 70px;
}

/* Left side */
.nav-left {
  display: flex;
  align-items: center;
  gap: 28px;
}

.logo-wordmark {
  font-weight: 800;
  font-size: 22px;
  letter-spacing: -0.03em;
  color: #0f172a;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.logo-dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: radial-gradient(circle at 30% 30%, #f9fafb, #a855f7);
  box-shadow: 0 0 0 4px rgba(168, 85, 247, 0.15);
}

/* Nav links */
.nav-links {
  display: flex;
  gap: 18px;
  align-items: center;
}

.nav-links a {
  position: relative;
  color: #111827;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  opacity: 0.9;
  padding-bottom: 4px;
  transition: opacity 0.18s ease, color 0.18s ease;
}

.nav-links a::after {
  content: "";
  position: absolute;
  left: 0;
  bottom: -4px;
  height: 2px;
  width: 0;
  border-radius: 999px;
  background: linear-gradient(90deg, #6366f1, #ec4899);
  transition: width 0.22s ease;
}

.nav-links a:hover {
  opacity: 1;
  color: #0f172a;
}

.nav-links a:hover::after {
  width: 100%;
}

.nav-links a.router-link-active {
  color: #4c1d95;
  opacity: 1;
}

.nav-links a.router-link-active::after {
  width: 100%;
}

/* Right side */
.nav-right {
  display: flex;
  gap: 10px;
  align-items: center;
}

/* Icon buttons */
.icon-btn,
.avatar-button {
  width: 44px;
  height: 44px;
  border-radius: 999px;
  border: 1px solid rgba(209, 213, 219, 0.9);
  background: radial-gradient(circle at 30% 20%, #ffffff, #e5e7eb);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.16s ease, box-shadow 0.16s ease, background 0.2s ease;
  box-shadow: 0 10px 24px rgba(148, 163, 184, 0.45);
}

.icon-btn:hover,
.avatar-button:hover {
  transform: translateY(-1px);
  background: radial-gradient(circle at 30% 20%, #ffffff, #d1d5db);
  box-shadow: 0 14px 30px rgba(148, 163, 184, 0.6);
}

.nav-icon {
  width: 26px;
  height: 26px;
  stroke-width: 1.8;
  color: #0f172a;
}

/* Header buttons for logged in users */
.header-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.profile-btn {
  background: #a855f7;
  color: white;
  box-shadow: 0 4px 12px rgba(168, 85, 247, 0.3);
}

.profile-btn:hover {
  background: #9333ea;
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(168, 85, 247, 0.4);
}

.dashboard-btn {
  background: white;
  color: #4b5563;
  border-color: #e5e7eb;
}

.dashboard-btn:hover {
  background: #f3e8ff;
  color: #7c3aed;
  border-color: #c4b5fd;
}

.logout-btn {
  background: white;
  color: #6b7280;
  border-color: #e5e7eb;
}

.logout-btn:hover {
  background: #fef2f2;
  color: #dc2626;
  border-color: #fecaca;
}

/* Small screens */
@media (max-width: 768px) {
  .nav-inner {
    height: 64px;
  }

  .nav-left {
    gap: 18px;
  }

  .nav-links {
    gap: 12px;
  }

  .nav-links a {
    font-size: 13px;
  }

  .logo-wordmark {
    font-size: 20px;
  }
}
</style>
