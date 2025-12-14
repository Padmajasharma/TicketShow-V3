import { createApp } from 'vue';
import App from './App.vue';
import { createRouter, createWebHistory } from 'vue-router';
import axios from 'axios';
import Home from './components/Home.vue';
import SignupForm from './components/SignupForm.vue';
import LoginForm from './components/LoginForm.vue';
import UserDashboard from './components/UserDashboard.vue';
import AdminDashboard from './components/AdminDashboard.vue';
import TheatreList from './components/TheatreList.vue';
import ShowList from './components/ShowList.vue';
import Movies from './components/Movies.vue';
import UserProfile from './components/UserProfile.vue';
import './assets/global.css';
import Concerts from './components/Concerts.vue';
import Plays from './components/Plays.vue';
import Events from './components/Events.vue';
import BookingPage from './components/BookingPage.vue';
import AdminAnalytics from './components/AdminAnalytics.vue';
import { isTokenExpired, clearAuthData, getTimeUntilExpiry } from './utils/auth';

// Configure API base URL from environment (Vercel/Netlify) or fallback to localhost for dev
const API_BASE_URL = process.env.VUE_APP_API_BASE_URL || 'http://localhost:5001';
axios.defaults.baseURL = API_BASE_URL;
window.axios = axios;

// Token expiration timer reference
let tokenExpirationTimer = null;

// Function to handle logout
function handleTokenExpiration(router) {
  clearAuthData();
  if (tokenExpirationTimer) {
    clearTimeout(tokenExpirationTimer);
    tokenExpirationTimer = null;
  }
  // Dispatch a custom event so components can react
  window.dispatchEvent(new CustomEvent('auth-expired'));
  router.push('/login');
}

// Function to set up token expiration timer
export function setupTokenExpirationTimer(router) {
  // Clear existing timer
  if (tokenExpirationTimer) {
    clearTimeout(tokenExpirationTimer);
    tokenExpirationTimer = null;
  }

  const token = localStorage.getItem('access_token');
  if (!token) return;

  // Check if already expired
  if (isTokenExpired(token)) {
    handleTokenExpiration(router);
    return;
  }

  // Set up timer for when token expires
  const timeUntilExpiry = getTimeUntilExpiry(token);
  if (timeUntilExpiry > 0) {
    // Friendly formatting: show hours+minutes when appropriate
    const minutes = Math.round(timeUntilExpiry / 1000 / 60);
    let humanReadable = `${minutes} minutes`;
    if (minutes >= 60) {
      const hours = Math.floor(minutes / 60);
      const rem = minutes % 60;
      humanReadable = `${hours}h ${rem}m`;
    }
    console.log(`Token will expire in ${humanReadable}`);

    tokenExpirationTimer = setTimeout(() => {
      console.log('Token expired - logging out');
      // Use a non-blocking notification where possible; fallback to alert
      try {
        window.dispatchEvent(new CustomEvent('auth-expired-notify', { detail: { message: 'Your session has expired. Please log in again.' } }));
      } catch (e) {
        alert('Your session has expired. Please log in again.');
      }
      handleTokenExpiration(router);
    }, timeUntilExpiry);
  }
}

// Set up axios interceptor for 401 responses
export function setupAxiosInterceptor(router) {
  axios.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response && error.response.status === 401) {
        const token = localStorage.getItem('access_token');
        // Only auto-logout if we had a token (not during login attempt)
        if (token) {
          console.log('Received 401 - token may be expired');
          handleTokenExpiration(router);
        }
      }
      return Promise.reject(error);
    }
  );
}

const routes = [
  { path: '/', component: Home },
  { path: '/signup', component: SignupForm },
  { path: '/login', component: LoginForm },
  { path: '/Userdashboard', component: UserDashboard },
  { path: '/Admindashboard', component: AdminDashboard },
  { path: '/theatres', component: TheatreList },
  { path: '/shows', component: ShowList },
  { path: '/movies', component: Movies },
  { path: '/userprofile', component: UserProfile },
  { path: '/concerts', component: Concerts },
  { path: '/plays', component: Plays },
  { path: '/events', component: Events },
  { path: '/book/:id', component: BookingPage, props: true }
  ,{ path: '/admin/analytics', component: AdminAnalytics }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// Set up axios interceptor to handle 401 responses
setupAxiosInterceptor(router);

// Set up token expiration timer if user is already logged in
setupTokenExpirationTimer(router);

// Listen for storage changes (e.g., login from another tab)
window.addEventListener('storage', (event) => {
  if (event.key === 'access_token') {
    if (event.newValue) {
      setupTokenExpirationTimer(router);
    }
  }
});

const app = createApp(App);
app.use(router);
// Also make axios available as $axios on the app instance
app.config.globalProperties.$axios = axios;
app.mount('#app');
