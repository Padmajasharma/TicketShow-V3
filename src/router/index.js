import { createRouter, createWebHistory } from 'vue-router';
import Home from '../components/Home.vue';
import SignupForm from '../components/SignupForm.vue';
import LoginForm from '../components/LoginForm.vue';
import UserDashboard from '../components/UserDashboard.vue';
import AdminDashboard from '../components/AdminDashboard.vue';
import AdminShows from '../components/AdminShows.vue';
import AdminTheatres from '../components/AdminTheatres.vue';
import SeatLayoutEditor from '../components/SeatLayoutEditor.vue';
import AdminStats from '../components/AdminStats.vue';
import Recommendations from '../components/Recommendations.vue';
import TheatreList from '../components/TheatreList.vue';
import ShowList from '../components/ShowList.vue';
import UserProfile from '../components/UserProfile.vue';
import Movies from '../components/Movies.vue';
import Concerts from '../components/Concerts.vue';
import Plays from '../components/Plays.vue';
import Events from '../components/Events.vue';
import BookingPage from '../components/BookingPage.vue';
import OtpTest from '../components/OtpTest.vue';
import AdminAnalytics from '../components/AdminAnalytics.vue';

const routes = [
  { path: '/', component: Home },
  { path: '/signup', component: SignupForm },
  { path: '/login', component: LoginForm },
  { path: '/userdashboard', component: UserDashboard },
  { path: '/admindashboard', component: AdminDashboard },
  { path: '/admin/shows', component: AdminShows },
  { path: '/admin/theatres', component: AdminTheatres },
  { path: '/admin/theatres/:id/seats', component: SeatLayoutEditor, name: 'seat-layout' },
  { path: '/admin/stats', component: AdminStats },
  { path: '/recommendations', component: Recommendations },
  { path: '/theatres', component: TheatreList },
  { path: '/shows', component: ShowList },
  { path: '/userprofile', component: UserProfile },
  { path: '/movies', component: Movies },
  { path: '/concerts', component: Concerts },
  { path: '/plays', component: Plays },
  { path: '/events', component: Events },
  { path: '/book/:id', component: BookingPage, name: 'booking' }
  ,{ path: '/dev/otp', component: OtpTest }
  ,{ path: '/admin/analytics', component: AdminAnalytics, name: 'admin-analytics' }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
