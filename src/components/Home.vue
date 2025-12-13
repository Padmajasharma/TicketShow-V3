<template>
  <div class="home">
    <!-- NAVBAR -->
    <AppHeader @toggle-search="toggleSearch" @go-profile="goProfile" />

    <main>
      <!-- HERO WELCOME -->
      <div class="container">
        <div class="welcome-card">
          <div class="welcome-decoration">
            <span class="deco-circle deco-1"></span>
            <span class="deco-circle deco-2"></span>
            <span class="deco-circle deco-3"></span>
          </div>
          <div class="welcome-content">
            <div class="welcome-badge">
              <span class="badge-icon">✨</span>
              <span>Your Entertainment Hub</span>
            </div>
            <h1 class="welcome-title">Welcome to <span class="highlight">NovaSeat</span></h1>
            <p class="welcome-subtitle">Discover and book your next unforgettable experience. From blockbuster premieres to intimate concerts.</p>
            <div class="hero-cta">
              <router-link to="/movies" class="cta-primary">Browse All Shows</router-link>
              <button class="cta-secondary" @click="toggleSearch">Search Events</button>
            </div>
          </div>
        </div>
      </div>

      <!-- FEATURED SPOTLIGHT -->
      <section class="section spotlight">
        <div class="container">
          <div class="spotlight-card" v-if="spotlightShow">
            <div class="spotlight-poster">
              <img :src="spotlightShow.posterUrl" :alt="spotlightShow.name" class="spotlight-img" />
              <div class="spotlight-gradient"></div>
            </div>
            <div class="spotlight-content">
              <span class="spotlight-badge">Featured</span>
              <h2 class="spotlight-title">{{ spotlightShow.name }}</h2>
              <p class="spotlight-meta">{{ spotlightShow.genre }} · {{ spotlightShow.year }} · ★ {{ spotlightShow.rating }}</p>
              <p class="spotlight-desc">{{ spotlightShow.description || 'An incredible experience awaits. Book your seats now and be part of something extraordinary.' }}</p>
              <button class="spotlight-btn" @click="goToShow(spotlightShow)">Get Tickets</button>
            </div>
          </div>
        </div>
      </section>

      <!-- QUICK STATS -->
      <section class="section stats-section">
        <div class="container">
          <div class="stats-grid">
            <div class="stat-card">
              <span class="stat-number">{{ platformStats.totalShows }}+</span>
              <span class="stat-label">Shows Available</span>
            </div>
            <div class="stat-card">
              <span class="stat-number">{{ platformStats.totalTheatres }}+</span>
              <span class="stat-label">Partner Venues</span>
            </div>
            <div class="stat-card">
              <span class="stat-number">{{ platformStats.citiesCovered }}+</span>
              <span class="stat-label">Cities Covered</span>
            </div>
            <div class="stat-card">
              <span class="stat-number">{{ platformStats.happyCustomers }}</span>
              <span class="stat-label">Happy Customers</span>
            </div>
          </div>
        </div>
      </section>

      <!-- HOW IT WORKS -->
      <section class="section how-it-works">
        <div class="container">
          <div class="section-header centered">
            <h2 class="section-heading">How It Works</h2>
            <span class="section-subtitle">Book your tickets in 3 simple steps</span>
          </div>
          <div class="steps-grid">
            <div class="step-card">
              <div class="step-number">1</div>
              <h3 class="step-title">Browse</h3>
              <p class="step-desc">Explore our curated collection of shows, concerts, plays, and events</p>
            </div>
            <div class="step-card">
              <div class="step-number">2</div>
              <h3 class="step-title">Select</h3>
              <p class="step-desc">Choose your preferred date, time, and seats at your favorite venue</p>
            </div>
            <div class="step-card">
              <div class="step-number">3</div>
              <h3 class="step-title">Book</h3>
              <p class="step-desc">Secure your tickets instantly and receive confirmation via email</p>
            </div>
          </div>
        </div>
      </section>

      <!-- TRENDING NOW (GRID) -->
      <section class="section trending">
        <div class="container">
          <div class="section-header">
            <h2 class="section-heading">Trending Now</h2>
            <router-link to="/movies" class="section-link">See all</router-link>
          </div>

          <div class="trending-grid">
            <div
              v-for="show in trendingShows.slice(0, 4)"
              :key="show.id"
              class="show-card"
              @click="goToShow(show)"
            >
              <div class="card-poster">
                <img :src="show.posterUrl" :alt="show.name" class="poster-img" />
                <div class="card-glow"></div>
                <div class="card-rating-pill">★ {{ show.rating }}</div>
              </div>
              <div class="card-info">
                <h3 class="card-title">{{ show.name }}</h3>
                <p class="card-meta">{{ show.genre }} · {{ show.year }}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

     

      <section class="section">
        <div class="container">
          <div class="section-header">
            <h2 class="section-heading">Concerts</h2>
            <router-link to="/concerts" class="section-link">See all</router-link>
          </div>
          <div class="trending-grid">
            <div v-for="c in concerts.slice(0, 8)" :key="'c' + c.id" class="show-card" @click="goToShow(c)">
              <div class="card-poster">
                  <img :src="resolvedImage(c.image, 'Concert', c.name)" :alt="c.name" class="poster-img" />
                <div class="card-glow"></div>
              </div>
              <div class="card-info">
                <h3 class="card-title">{{ c.name }}</h3>
                <p class="card-meta">{{ c.tags || 'Concert' }}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="section">
        <div class="container">
          <div class="section-header">
            <h2 class="section-heading">Plays</h2>
            <router-link to="/plays" class="section-link">See all</router-link>
          </div>
          <div class="trending-grid">
            <div v-for="p in plays.slice(0, 8)" :key="'p' + p.id" class="show-card" @click="goToShow(p)">
              <div class="card-poster">
                  <img :src="resolvedImage(p.image, 'Play', p.name)" :alt="p.name" class="poster-img" />
                <div class="card-glow"></div>
              </div>
              <div class="card-info">
                <h3 class="card-title">{{ p.name }}</h3>
                <p class="card-meta">{{ p.tags || 'Play' }}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="section">
        <div class="container">
          <div class="section-header">
            <h2 class="section-heading">Events</h2>
            <router-link to="/events" class="section-link">See all</router-link>
          </div>
          <div class="trending-grid">
            <div v-for="e in events.slice(0, 8)" :key="'e' + e.id" class="show-card" @click="goToShow(e)">
              <div class="card-poster">
                  <img :src="resolvedImage(e.image, 'Event', e.name)" :alt="e.name" class="poster-img" />
                <div class="card-glow"></div>
              </div>
              <div class="card-info">
                <h3 class="card-title">{{ e.name }}</h3>
                <p class="card-meta">{{ e.tags || 'Event' }}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- UPCOMING RELEASES (HORIZONTAL) -->
      <section class="section upcoming">
        <div class="container">
          <div class="section-header">
            <h2 class="section-heading">Upcoming Releases</h2>
            <a href="#" class="section-link">See calendar</a>
          </div>

          <div class="upcoming-scroll">
            <div
              v-for="show in upcomingShows.slice(0, 6)"
              :key="'up' + show.id"
              class="upcoming-item"
            >
              <div class="upcoming-poster">
                <img :src="show.posterUrl" :alt="show.name" class="poster-img" />
                <div class="upcoming-overlay">
                  <p class="upcoming-title">{{ show.name }}</p>
                  <p class="upcoming-genre">{{ show.genre }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- TOP PICKS FOR YOU -->
      <section class="section top-picks">
        <div class="container">
          <div class="section-header">
            <h2 class="section-heading">Top Picks for You</h2>
            <span class="section-subtitle">Curated from what people are loving.</span>
          </div>

          <div class="picks-grid">
            <div
              v-for="show in trendingShows.slice(0, 3)"
              :key="'pick' + show.id"
              class="pick-card"
              @click="goToShow(show)"
            >
              <div class="pick-badge">Recommended</div>
              <div class="pick-poster">
                <img :src="show.posterUrl" :alt="show.name" class="poster-img" />
              </div>
              <div class="pick-info">
                <h3 class="pick-title">{{ show.name }}</h3>
                <p class="pick-desc">{{ show.genre }} • Highly rated</p>
                <button class="pick-action">Explore</button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- POPULAR ARTISTS (CIRCLES) -->
      <section class="section artists">
        <div class="container">
          <div class="section-header">
            <h2 class="section-heading">Popular Artists & Creators</h2>
            <span class="section-subtitle">Faces behind the stories you love.</span>
          </div>

          <div class="artists-scroll">
            <div
              v-for="(artist, idx) in artists.slice(0, 8)"
              :key="'artist' + artist.id"
              class="artist-item"
            >
              <div class="artist-circle" :style="{ background: getArtistGradient(idx) }">
                <div class="artist-inner">
                  <img :src="artist.imageUrl" :alt="artist.name" class="artist-img" />
                </div>
              </div>
              <p class="artist-name">{{ artist.name }}</p>
              <p class="artist-role">{{ artist.role }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- SEARCH OVERLAY -->
      <SearchOverlay v-model="showSearchOverlay" :items="allShows" @select="goToShow" />

      <!-- FOOTER -->
      <footer class="site-footer">
        <div class="footer-grid">
          <div>
            <div class="logo-wordmark footer-logo">NovaSeat</div>
            <div class="footer-text">
              Find, book and enjoy premium cinema & events with a beautifully simple flow.
            </div>
          </div>
          <div class="footer-links">
            <h4>Explore</h4>
            <a href="#">Movies</a>
            <a href="#">Concerts</a>
            <a href="#">Plays</a>
          </div>
          <div class="footer-links">
            <h4>Support</h4>
            <a href="#">Help Center</a>
            <a href="#">Contact</a>
          </div>
          <div class="footer-links">
            <h4>Social</h4>
            <a href="#">Twitter</a>
            <a href="#">Instagram</a>
          </div>
        </div>
      </footer>
    </main>
  </div>
</template>

<script>
import AppHeader from './AppHeader.vue';
import SearchOverlay from './SearchOverlay.vue';
import { isAuthenticated } from '@/utils/auth';

export default {
  name: 'Home',
  components: { AppHeader, SearchOverlay },
  data() {
    return {
      activeCategory: 'All',
      categories: ['All', 'Movies', 'Plays', 'Concerts', 'Events'],
      searchQuery: '',
      showSearchOverlay: false,
      movies: [],
      concerts: [],
      plays: [],
      events: [],
      platformStats: {
        totalShows: 150,
        totalTheatres: 45,
        citiesCovered: 12,
        happyCustomers: '10K'
      },
      spotlightShow: {
        id: 1096197,
        name: 'Dune: Part Two',
        genre: 'Sci-Fi',
        year: '2024',
        rating: 8.0,
        posterUrl: 'https://image.tmdb.org/t/p/w500/1pdfLvkbY9ohJlCjQH2CZjjYVvJ.jpg',
        description: 'Paul Atreides unites with the Fremen to seek revenge against those who destroyed his family, while facing a choice between the love of his life and the fate of the universe.'
      },
      trendingShows: [
        {
          id: 1096197,
          name: 'Dune: Part Two',
          genre: 'Sci-Fi',
          year: '2024',
          rating: 8.0,
          posterUrl: 'https://image.tmdb.org/t/p/w500/1pdfLvkbY9ohJlCjQH2CZjjYVvJ.jpg'
        },
        {
          id: 1054588,
          name: 'Inside Out 2',
          genre: 'Animation',
          year: '2024',
          rating: 8.3,
          posterUrl: 'https://image.tmdb.org/t/p/w500/vpnVM9B6NMmQpWeZvzLvDESb2QY.jpg'
        },
        {
          id: 912908,
          name: 'Deadpool & Wolverine',
          genre: 'Action',
          year: '2024',
          rating: 7.9,
          posterUrl: 'https://image.tmdb.org/t/p/w500/8cdWjvZQUExUUTzyp4t6EDMubfO.jpg'
        },
        {
          id: 1184918,
          name: 'Wicked',
          genre: 'Musical',
          year: '2024',
          rating: 8.1,
          posterUrl: 'https://image.tmdb.org/t/p/w500/xDGbZ0JJ3mYaGKy4Nzd9Kph6M9L.jpg'
        }
      ],
      upcomingShows: [
        {
          id: 550,
          name: 'Fight Club',
          genre: 'Drama',
          year: '1999',
          rating: 8.8,
          posterUrl: 'https://image.tmdb.org/t/p/w500/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg'
        },
        {
          id: 278,
          name: 'The Shawshank Redemption',
          genre: 'Drama',
          year: '1994',
          rating: 9.3,
          posterUrl: 'https://image.tmdb.org/t/p/w500/9cqNxx0GxF0bflZmeSMuL5tnGzr.jpg'
        },
        {
          id: 238,
          name: 'The Godfather',
          genre: 'Crime',
          year: '1972',
          rating: 9.2,
          posterUrl: 'https://image.tmdb.org/t/p/w500/e5iVtjkjM30znn86JsvkBYtvEo1.jpg'
        },
        {
          id: 240,
          name: 'The Godfather: Part II',
          genre: 'Crime',
          year: '1974',
          rating: 9.0,
          posterUrl: 'https://image.tmdb.org/t/p/w500/hek3koDUyRQk7FIhPXsa6mT2Zc3.jpg'
        },
        {
          id: 424,
          name: "Schindler's List",
          genre: 'Drama',
          year: '1993',
          rating: 9.0,
          posterUrl: 'https://image.tmdb.org/t/p/w500/sF1U4EUQS8YHUYjNl3pMGNIQyr0.jpg'
        },
        {
          id: 389,
          name: '12 Angry Men',
          genre: 'Drama',
          year: '1957',
          rating: 9.0,
          posterUrl: 'https://image.tmdb.org/t/p/w500/ow3wq89wM8qd5X7hWKxiRfsFf9C.jpg'
        }
      ],
      artists: [
  {
    id: 6193,
    name: 'Leonardo DiCaprio',
    role: 'Actor',
    imageUrl: 'https://image.tmdb.org/t/p/w300/wo2hJpn04vbtmh0B9utCFdsQhxM.jpg'
  },
  {
    id: 6384,
    name: 'Keanu Reeves',
    role: 'Actor',
    imageUrl: 'https://image.tmdb.org/t/p/w300/8RZLOyYGsoRe9p44q3xin9QkMHv.jpg'
  },
  {
    id: 5064,
    name: 'Meryl Streep',
    role: 'Actress',
    imageUrl: 'https://image.tmdb.org/t/p/w300/emAAzyK1rJ6aiMi0wsWYp51EC3h.jpg'
  },
  {
    id: 500,
    name: 'Tom Cruise',
    role: 'Actor',
    imageUrl: 'https://image.tmdb.org/t/p/w300/3mShHjSQR7NXOVbdTu5rT2Qd0MN.jpg'
  },
  {
    id: 287,
    name: 'Brad Pitt',
    role: 'Actor',
    imageUrl: 'https://image.tmdb.org/t/p/w300/nWyL0YMgsBOsvX4gVSFB16VfnPU.jpg'
  },
  {
    id: 1136406,
    name: 'Tom Holland',
    role: 'Actor',
    imageUrl: 'https://image.tmdb.org/t/p/w300/4jG9XoIjrkIrkYXB9IjegsomL46.jpg'
  },
  {
    id: 819,
    name: 'Edward Norton',
    role: 'Actor',
    imageUrl: 'https://image.tmdb.org/t/p/w300/8nytsqL59SFJTVYVrN72k6qkGgJ.jpg'
  },
  {
    id: 18918,
    name: 'Dwayne Johnson',
    role: 'Actor',
    imageUrl: 'https://image.tmdb.org/t/p/w300/5QApZVV8FUFlVxQpIK3Ew6cqotq.jpg'
  }
]

    };
  },
  created() {
    this.fetchShows();
  },
  computed: {
    allShows() {
      // Combine all shows from different categories for search
      const combined = [
        ...this.movies,
        ...this.concerts,
        ...this.plays,
        ...this.events
      ];
      // Remove duplicates by id
      const seen = new Set();
      return combined.filter(s => {
        if (seen.has(s.id)) return false;
        seen.add(s.id);
        return true;
      });
    },
    filteredShows() {
      const q = this.searchQuery.trim().toLowerCase();
      return this.trendingShows.filter((s) => {
        const matchesQuery =
          !q || s.name.toLowerCase().includes(q) || s.genre.toLowerCase().includes(q);
        return matchesQuery;
      });
    }
  },
  methods: {
    // Fetch and split shows by tag
    async fetchShows() {
      const token = localStorage.getItem('access_token');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      // Fetch all shows and split into categories via axios (uses axios.defaults.baseURL)
      try {
        const resp = await axios.get('/shows', { headers });
        const data = resp.data;
        const shows = Array.isArray(data) ? data : [];

        // Populate trending shows from database
        if (shows.length > 0) {
          this.trendingShows = shows.slice(0, 8).map(s => ({
            id: s.id,
            name: s.name,
            genre: s.tags || 'General',
            year: s.release_date ? s.release_date.split('-')[0] : new Date().getFullYear().toString(),
            rating: s.tmdb_rating || s.rating || 0,
            posterUrl: s.image || this.placeholder
          }));

          // Set spotlight show to first show with an image
          const spotShow = shows.find(s => s.image) || shows[0];
          if (spotShow) {
            this.spotlightShow = {
              id: spotShow.id,
              name: spotShow.name,
              genre: spotShow.tags || 'General',
              year: spotShow.release_date ? spotShow.release_date.split('-')[0] : new Date().getFullYear().toString(),
              rating: spotShow.tmdb_rating || spotShow.rating || 0,
              posterUrl: spotShow.image || this.placeholder,
              description: spotShow.overview || 'An incredible experience awaits. Book your seats now!'
            };
          }
        }

        const byTag = (tag) => shows.filter(s => (s.tags || '').toLowerCase().includes(tag));

        // Deduplicate by id
        const dedupeById = (arr) => {
          const seen = new Set();
          return arr.filter(item => {
            if (seen.has(item.id)) return false;
            seen.add(item.id);
            return true;
          });
        };

        // Movies: include various genres but exclude concerts, plays, events
        const movieTags = ['movie', 'animation', 'comedy', 'drama', 'action', 'thriller', 'horror', 'sci-fi', 'adventure'];
        const movieShows = shows.filter(s => {
          const tags = (s.tags || '').toLowerCase();
          return movieTags.some(tag => tags.includes(tag)) && !tags.includes('concert') && !tags.includes('play') && !tags.includes('event');
        }).map(s => ({ id: s.id, name: s.name, tags: s.tags, image: s.image }));
        this.movies = dedupeById(movieShows);

        // Concerts: include concert/music but exclude plays/theatre/musical
        const concertShows = shows.filter(s => {
          const tags = (s.tags || '').toLowerCase();
          return (tags.includes('concert') || tags.includes('live')) && 
                 !tags.includes('play') && !tags.includes('theatre') && !tags.includes('theater');
        }).map(s => ({ id: s.id, name: s.name, tags: s.tags, image: s.image }));
        this.concerts = dedupeById(concertShows);

        // Plays: include play/theatre/musical but exclude concerts
        const playShows = shows.filter(s => {
          const tags = (s.tags || '').toLowerCase();
          return (tags.includes('play') || tags.includes('theatre') || tags.includes('theater') || tags.includes('musical')) && 
                 !tags.includes('concert');
        }).map(s => ({ id: s.id, name: s.name, tags: s.tags, image: s.image }));
        this.plays = dedupeById(playShows);

        this.events = byTag('event').map(s => ({ id: s.id, name: s.name, tags: s.tags, image: s.image }));

        // Ensure Tyla appears in concerts if not present in backend data
        const hasTyla = this.concerts.some(c => (c.name || '').toLowerCase().includes('tyla'));
        if (!hasTyla) {
          this.concerts.unshift({ id: 'local-tyla', name: 'Tyla', tags: 'Concert', image: '' });
        }
        // Ensure sample events (Tech Expo, etc) appear
        const sampleEvents = [
          { id: 'local-techexpo', name: 'Tech Expo 2025', tags: 'Event', image: 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=500' },
          { id: 'local-comiccon', name: 'Comic Con', tags: 'Event', image: 'https://images.unsplash.com/photo-1612036782180-6f0b6cd846fe?w=500' },
          { id: 'local-foodfest', name: 'Food Festival', tags: 'Event', image: 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=500' }
        ];
        const existingEventNames = new Set(this.events.map(e => (e.name || '').toLowerCase()));
        sampleEvents.forEach(se => {
          if (!existingEventNames.has(se.name.toLowerCase())) {
            this.events.push(se);
          }
        });
      } catch (err) {
        console.error('Failed to load shows for home', err);
      }
    },
    toggleSearch() {
      this.showSearchOverlay = true;
    },
    closeSearch() {
      this.showSearchOverlay = false;
    },
    performSearch() {
      // Search results are shown in real-time via filteredShows
      // When a result is clicked, goToShow will be called
    },
    setCategory(c) {
      this.activeCategory = c;
      this.searchQuery = '';
    },
    goToShow(show) {
      try {
        if (!isAuthenticated()) {
          this.$router.push({ path: '/login', query: { redirect: `/book/${show.id}` } });
        } else {
          this.$router.push(`/book/${show.id}`);
        }
      } catch (e) {
        console.warn('Router not available or navigation failed', e);
      }
    },
    goProfile() {
      try {
        const token = localStorage.getItem('access_token');
        
        if (token) {
          // User is logged in, redirect to user dashboard
          this.$router.push('/userdashboard');
        } else {
          // User is not logged in, redirect to login form
          this.$router.push('/login');
        }
      } catch (e) {
        console.warn('Router navigation failed', e);
      }
    },
    // Prefer local assets for certain known shows
    localAssetFor(name) {
      const key = (name || '').toLowerCase();
      // Map known show names to local assets
      const map = {
        'arijit singh': require('@/assets/arijit.jpeg'),
        'tyla': require('@/assets/Tyla.jpg'),
        'hamlet': require('@/assets/Hamlet.jpg')
      };
      // exact match
      if (map[key]) return map[key];
      // fuzzy contains
      if (key.includes('arijit')) return require('@/assets/arijit.jpeg');
      if (key.includes('tyla')) return require('@/assets/Tyla.jpg');
      if (key.includes('hamlet')) return require('@/assets/Hamlet.jpg');
      // Online images for concerts without local assets
      if (key.includes('coldplay')) return 'https://images.unsplash.com/photo-1470229722913-7c0e2dbbafd3?w=500';
      if (key.includes('taylor swift')) return 'https://images.unsplash.com/photo-1501386761578-eac5c94b800a?w=500';
      // Online images for events
      if (key.includes('tech expo')) return 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=500';
      if (key.includes('comic con')) return 'https://images.unsplash.com/photo-1612036782180-6f0b6cd846fe?w=500';
      if (key.includes('food festival')) return 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=500';
      return null;
    },
    resolvedImage(url, fallbackLabel, name) {
      const local = this.localAssetFor(name);
      if (local) return local;
      if (url && typeof url === 'string' && url.length > 0) return url;
      return "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='450' viewBox='0 0 300 450'%3E%3Crect fill='%23374151' width='300' height='450'/%3E%3Ctext fill='%239ca3af' font-family='sans-serif' font-size='16' x='50%25' y='50%25' text-anchor='middle' dy='.3em'%3EShow%3C/text%3E%3C/svg%3E";
    },
    getArtistGradient(index) {
      const gradients = [
        'linear-gradient(135deg,#D9D4F1,#FADCD9)',
        'linear-gradient(135deg,#DFF5E3,#D7EAF8)',
        'linear-gradient(135deg,#FFE4E6,#E8F3FF)',
        'linear-gradient(135deg,#F0E6FF,#FFF5CC)',
        'linear-gradient(135deg,#D7EAF8,#FADCD9)',
        'linear-gradient(135deg,#E8F3FF,#D9D4F1)',
        'linear-gradient(135deg,#FFF5CC,#FADCD9)',
        'linear-gradient(135deg,#F0E6FF,#DFF5E3)'
      ];
      return gradients[index % gradients.length];
    }
  }
};
</script>

<style scoped>
.home {
  --primary-text: #0f172a;
  --secondary-text: #6b7280;
  --border-color: #e5e7eb;
  --pastel-lilac: #a855f7;
  --font-heading: system-ui, -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Inter', 'Segoe UI', sans-serif;
  --font-body: system-ui, -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', sans-serif;

  min-height: 100vh;
  background:
    radial-gradient(circle at 0% 0%, rgba(217, 212, 241, 0.9) 0, transparent 55%),
    radial-gradient(circle at 100% 0%, rgba(250, 220, 217, 0.9) 0, transparent 55%),
    radial-gradient(circle at 0% 100%, rgba(215, 234, 248, 0.9) 0, transparent 55%),
    #f9fafb;
}

/* Layout */
.container {
  max-width: 1180px;
  margin: 0 auto;
  padding: 0 20px;
}

/* ============ WELCOME CARD ============ */
.welcome-card {
  position: relative;
  margin: 20px 0 40px;
  padding: 40px 45px;
  background: linear-gradient(135deg, 
    rgba(168, 85, 247, 0.08) 0%,
    rgba(236, 72, 153, 0.06) 50%,
    rgba(59, 130, 246, 0.08) 100%);
  border-radius: 24px;
  border: 1px solid rgba(168, 85, 247, 0.15);
  overflow: hidden;
  box-shadow: 
    0 4px 20px rgba(168, 85, 247, 0.08),
    0 8px 40px rgba(236, 72, 153, 0.05);
}

.welcome-decoration {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  pointer-events: none;
  overflow: hidden;
}

.deco-circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.4;
}

.deco-1 {
  width: 300px;
  height: 300px;
  top: -150px;
  right: -50px;
  background: radial-gradient(circle, rgba(168, 85, 247, 0.3) 0%, transparent 70%);
}

.deco-2 {
  width: 200px;
  height: 200px;
  bottom: -100px;
  left: -50px;
  background: radial-gradient(circle, rgba(236, 72, 153, 0.25) 0%, transparent 70%);
}

.deco-3 {
  width: 150px;
  height: 150px;
  top: 50%;
  right: 20%;
  background: radial-gradient(circle, rgba(59, 130, 246, 0.2) 0%, transparent 70%);
}

.welcome-content {
  position: relative;
  z-index: 1;
}

.welcome-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(168, 85, 247, 0.12);
  border-radius: 50px;
  font-size: 13px;
  font-weight: 600;
  color: var(--pastel-lilac);
  margin-bottom: 16px;
}

.badge-icon {
  font-size: 14px;
}

.welcome-title {
  font-family: var(--font-heading);
  font-size: 42px;
  font-weight: 800;
  letter-spacing: -1px;
  color: var(--primary-text);
  margin: 0 0 12px;
  line-height: 1.1;
}

.welcome-title .highlight {
  background: linear-gradient(135deg, var(--pastel-lilac) 0%, #ec4899 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.welcome-subtitle {
  font-size: 17px;
  color: var(--secondary-text);
  margin: 0 0 28px;
  max-width: 500px;
  line-height: 1.6;
}

.welcome-features {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  color: var(--primary-text);
  border: 1px solid rgba(209, 213, 219, 0.5);
  transition: all 0.2s ease;
}

.feature-item:hover {
  background: white;
  border-color: var(--pastel-lilac);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(168, 85, 247, 0.15);
}

.feature-icon {
  font-size: 18px;
}

@media (max-width: 768px) {
  .welcome-card {
    padding: 30px 25px;
    margin: 15px 0 30px;
  }
  .welcome-title {
    font-size: 28px;
  }
  .welcome-subtitle {
    font-size: 15px;
  }
  .welcome-features {
    gap: 8px;
  }
  .feature-item {
    padding: 8px 14px;
    font-size: 13px;
  }
}

/* ============ HERO CTA BUTTONS ============ */
.hero-cta {
  display: flex;
  gap: 12px;
  margin-top: 8px;
}

.cta-primary {
  padding: 14px 28px;
  background: linear-gradient(135deg, var(--pastel-lilac) 0%, #ec4899 100%);
  color: white;
  font-weight: 600;
  font-size: 15px;
  border-radius: 12px;
  text-decoration: none;
  transition: all 0.2s ease;
  box-shadow: 0 4px 15px rgba(168, 85, 247, 0.3);
}

.cta-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(168, 85, 247, 0.4);
}

.cta-secondary {
  padding: 14px 28px;
  background: rgba(255, 255, 255, 0.9);
  color: var(--primary-text);
  font-weight: 600;
  font-size: 15px;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cta-secondary:hover {
  border-color: var(--pastel-lilac);
  background: white;
}

/* ============ FEATURED SPOTLIGHT ============ */
.spotlight {
  padding: 40px 0;
}

.spotlight-card {
  position: relative;
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 40px;
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.03) 0%, rgba(168, 85, 247, 0.05) 100%);
  border-radius: 24px;
  padding: 30px;
  border: 1px solid rgba(168, 85, 247, 0.1);
  overflow: hidden;
}

.spotlight-poster {
  position: relative;
  border-radius: 16px;
  overflow: hidden;
  aspect-ratio: 2/3;
}

.spotlight-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.spotlight-gradient {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(0,0,0,0.3) 0%, transparent 50%);
}

.spotlight-content {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 20px 0;
}

.spotlight-badge {
  display: inline-block;
  width: fit-content;
  padding: 6px 14px;
  background: linear-gradient(135deg, var(--pastel-lilac) 0%, #ec4899 100%);
  color: white;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-radius: 20px;
  margin-bottom: 16px;
}

.spotlight-title {
  font-family: var(--font-heading);
  font-size: 36px;
  font-weight: 800;
  color: var(--primary-text);
  margin: 0 0 12px;
  letter-spacing: -0.5px;
}

.spotlight-meta {
  font-size: 15px;
  color: var(--secondary-text);
  margin: 0 0 16px;
}

.spotlight-desc {
  font-size: 16px;
  line-height: 1.7;
  color: var(--secondary-text);
  margin: 0 0 24px;
  max-width: 500px;
}

.spotlight-btn {
  width: fit-content;
  padding: 14px 32px;
  background: linear-gradient(135deg, var(--pastel-lilac) 0%, #ec4899 100%);
  color: white;
  font-weight: 600;
  font-size: 15px;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 15px rgba(168, 85, 247, 0.3);
}

.spotlight-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(168, 85, 247, 0.4);
}

@media (max-width: 768px) {
  .spotlight-card {
    grid-template-columns: 1fr;
    gap: 24px;
  }
  .spotlight-poster {
    max-width: 200px;
    margin: 0 auto;
  }
  .spotlight-title {
    font-size: 24px;
  }
  .hero-cta {
    flex-direction: column;
  }
}

/* ============ QUICK STATS ============ */
.stats-section {
  padding: 40px 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(168, 85, 247, 0.1);
  border-radius: 16px;
  padding: 28px 20px;
  text-align: center;
  transition: all 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(168, 85, 247, 0.12);
  border-color: rgba(168, 85, 247, 0.2);
}

.stat-number {
  display: block;
  font-family: var(--font-heading);
  font-size: 32px;
  font-weight: 800;
  background: linear-gradient(135deg, var(--pastel-lilac) 0%, #ec4899 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 6px;
}

.stat-label {
  font-size: 14px;
  color: var(--secondary-text);
  font-weight: 500;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .stat-number {
    font-size: 24px;
  }
}

/* ============ HOW IT WORKS ============ */
.how-it-works {
  padding: 50px 0;
}

.section-header.centered {
  text-align: center;
  margin-bottom: 40px;
}

.section-header.centered .section-heading {
  margin-bottom: 8px;
}

.section-header.centered .section-subtitle {
  color: var(--secondary-text);
  font-size: 15px;
}

.steps-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 30px;
}

.step-card {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(168, 85, 247, 0.1);
  border-radius: 20px;
  padding: 32px 24px;
  text-align: center;
  transition: all 0.2s ease;
}

.step-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 30px rgba(168, 85, 247, 0.1);
}

.step-number {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, var(--pastel-lilac) 0%, #ec4899 100%);
  color: white;
  font-size: 20px;
  font-weight: 700;
  border-radius: 50%;
  margin-bottom: 20px;
}

.step-title {
  font-family: var(--font-heading);
  font-size: 20px;
  font-weight: 700;
  color: var(--primary-text);
  margin: 0 0 12px;
}

.step-desc {
  font-size: 14px;
  line-height: 1.6;
  color: var(--secondary-text);
  margin: 0;
}

@media (max-width: 768px) {
  .steps-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
}

/* WELCOME BANNER */
.welcome-banner {
  padding: 56px 0 32px;
}

.welcome-inner {
  display: flex;
  align-items: center;
  justify-content: center;
}

.welcome-text {
  text-align: center;
  padding: 26px 32px;
  border-radius: 28px;
  background:
    radial-gradient(circle at 0 0, rgba(217, 212, 241, 0.9), transparent 60%),
    radial-gradient(circle at 100% 100%, rgba(250, 220, 217, 0.9), transparent 60%),
    rgba(255, 255, 255, 0.96);
  box-shadow:
    0 24px 70px rgba(148, 163, 184, 0.45),
    0 0 0 1px rgba(255, 255, 255, 0.8);
  max-width: 720px;
  position: relative;
  overflow: hidden;
}

.welcome-text::before {
  content: '✦';
  position: absolute;
  top: 16px;
  right: 18px;
  font-size: 18px;
  color: rgba(168, 85, 247, 0.7);
  filter: drop-shadow(0 0 6px rgba(168, 85, 247, 0.6));
}

.welcome-headline {
  position: relative;
  font-family: var(--font-heading);
  font-size: 34px;
  font-weight: 800;
  letter-spacing: -0.7px;
  color: var(--primary-text);
  margin: 0 0 10px 0;
  line-height: 1.2;
}

.welcome-tagline {
  position: relative;
  font-family: var(--font-body);
  font-size: 15px;
  color: var(--secondary-text);
  margin: 0;
  max-width: 540px;
  margin-inline: auto;
  line-height: 1.5;
}

/* CATEGORY PILLS */
.category-section {
  padding: 18px 0 36px;
}

.category-pills {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: center;
}

.pill {
  padding: 9px 22px;
  border-radius: 999px;
  border: 1px solid rgba(209, 213, 219, 0.9);
  background: rgba(255, 255, 255, 0.96);
  color: var(--secondary-text);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.25s ease;
  font-family: var(--font-body);
  box-shadow: 0 4px 12px rgba(148, 163, 184, 0.25);
  backdrop-filter: blur(10px);
}

.pill:hover {
  border-color: var(--pastel-lilac);
  color: var(--primary-text);
  transform: translateY(-2px);
  box-shadow: 0 10px 24px rgba(185, 167, 245, 0.35);
}

.pill.active {
  background: linear-gradient(135deg, var(--pastel-lilac), #ec4899);
  color: #f9fafb;
  border-color: transparent;
  box-shadow: 0 12px 30px rgba(185, 167, 245, 0.5);
}

/* SECTION BASE */
.section {
  padding: 44px 0;
}

.section-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 22px;
  flex-wrap: wrap;
}

.section-heading {
  font-family: var(--font-heading);
  font-size: 26px;
  font-weight: 700;
  color: var(--primary-text);
  margin: 0;
}

.section-subtitle {
  font-size: 13px;
  color: var(--secondary-text);
}

.section-link {
  font-size: 14px;
  text-decoration: none;
  color: var(--pastel-lilac);
  font-weight: 500;
}

/* TRENDING */
.trending {
  background:
    radial-gradient(circle at 0 0, rgba(217, 212, 241, 0.55), transparent 60%),
    radial-gradient(circle at 100% 100%, rgba(250, 220, 217, 0.45), transparent 60%),
    rgba(255, 255, 255, 0.94);
  border-radius: 28px;
  margin: 0 20px;
  box-shadow:
    0 20px 70px rgba(148, 163, 184, 0.45),
    0 0 0 1px rgba(255, 255, 255, 0.85);
}

.trending .container {
  padding-top: 26px;
  padding-bottom: 28px;
}

.trending-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 22px;
}

.show-card {
  cursor: pointer;
  transition: transform 0.3s ease, filter 0.3s ease;
}

.show-card:hover {
  transform: translateY(-8px);
  filter: drop-shadow(0 18px 40px rgba(15, 23, 42, 0.38));
}

.card-poster {
  position: relative;
  border-radius: 20px;
  overflow: hidden;
  margin-bottom: 12px;
  background: radial-gradient(circle at 10% 0, #e5e7eb, #0f172a);
}

.card-glow {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 10% 0, rgba(185, 167, 245, 0.55), transparent 60%),
    radial-gradient(circle at 90% 100%, rgba(248, 187, 208, 0.55), transparent 65%);
  mix-blend-mode: screen;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.35s ease;
}

.show-card:hover .card-glow {
  opacity: 1;
}

.card-rating-pill {
  position: absolute;
  right: 10px;
  top: 10px;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.9);
  color: #f9fafb;
  font-size: 11px;
  font-weight: 600;
}

.poster-img {
  width: 100%;
  aspect-ratio: 2 / 3;
  object-fit: cover;
  display: block;
  transform: scale(1.02);
  transition: transform 0.35s ease;
}

.show-card:hover .poster-img {
  transform: scale(1.06);
}

.card-info {
  padding: 2px 2px 0;
}

.card-title {
  font-family: var(--font-heading);
  font-size: 15px;
  font-weight: 700;
  color: var(--primary-text);
  margin: 0 0 4px 0;
  line-height: 1.25;
}

.card-meta {
  font-size: 13px;
  color: var(--secondary-text);
  margin: 0 0 4px 0;
}

/* UPCOMING */
.upcoming .section-heading {
  margin-bottom: 0;
}

.upcoming-scroll {
  display: flex;
  gap: 20px;
  overflow-x: auto;
  padding-bottom: 10px;
  -webkit-overflow-scrolling: touch;
}

.upcoming-scroll::-webkit-scrollbar {
  height: 6px;
}

.upcoming-scroll::-webkit-scrollbar-track {
  background: rgba(185, 167, 245, 0.15);
  border-radius: 3px;
}

.upcoming-scroll::-webkit-scrollbar-thumb {
  background: var(--pastel-lilac);
  border-radius: 3px;
}

.upcoming-item {
  flex-shrink: 0;
  min-width: 240px;
  width: 240px;
}

.upcoming-poster {
  position: relative;
  border-radius: 20px;
  overflow: hidden;
  height: 340px;
  box-shadow: 0 18px 46px rgba(15, 23, 42, 0.5);
}

.upcoming-poster .poster-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.upcoming-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    180deg,
    rgba(15, 23, 42, 0.05) 0%,
    rgba(15, 23, 42, 0.96) 100%
  );
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  padding: 16px;
  color: white;
}

.upcoming-title {
  font-weight: 700;
  font-size: 14px;
  margin: 0 0 3px 0;
}

.upcoming-genre {
  font-size: 12px;
  opacity: 0.9;
  margin: 0;
}

/* TOP PICKS */
.top-picks {
  padding-top: 52px;
}

.picks-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.pick-card {
  position: relative;
  border-radius: 24px;
  background:
    radial-gradient(circle at 0 0, rgba(217, 212, 241, 0.9), transparent 60%),
    rgba(255, 255, 255, 0.96);
  box-shadow:
    0 20px 55px rgba(148, 163, 184, 0.45),
    0 0 0 1px rgba(255, 255, 255, 0.9);
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.pick-card:hover {
  transform: translateY(-6px);
  box-shadow:
    0 26px 70px rgba(148, 163, 184, 0.55),
    0 0 0 1px rgba(255, 255, 255, 1);
}

.pick-badge {
  position: absolute;
  top: 14px;
  left: 14px;
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(185, 167, 245, 0.98);
  color: #f9fafb;
  font-size: 11px;
  font-weight: 600;
}

.pick-poster .poster-img {
  border-radius: 24px 24px 0 0;
}

.pick-info {
  padding: 14px 16px 16px;
}

.pick-title {
  margin: 0 0 4px;
  font-size: 15px;
  font-weight: 700;
  color: var(--primary-text);
}

.pick-desc {
  margin: 0 0 10px;
  font-size: 13px;
  color: var(--secondary-text);
}

.pick-action {
  border: none;
  background: rgba(185, 167, 245, 0.18);
  color: var(--pastel-lilac);
  font-size: 13px;
  font-weight: 600;
  padding: 7px 14px;
  border-radius: 999px;
  cursor: pointer;
}

/* ARTISTS */
.artists {
  padding-top: 52px;
}

.artists-scroll {
  display: flex;
  gap: 20px;
  overflow-x: auto;
  padding-bottom: 10px;
  -webkit-overflow-scrolling: touch;
}

.artist-item {
  flex-shrink: 0;
  text-align: center;
  min-width: 120px;
}

.artist-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%; /* true circle */
  padding: 3px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow:
    0 16px 40px rgba(148, 163, 184, 0.55),
    0 0 0 1px rgba(255, 255, 255, 0.9);
}

.artist-inner {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: rgba(15, 23, 42, 0.85);
  overflow: hidden;
  display: flex;
}

.artist-img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  display: block;
}

.artist-name {
  margin: 10px 0 2px;
  font-size: 14px;
  font-weight: 600;
  color: var(--primary-text);
}

.artist-role {
  margin: 0;
  font-size: 12px;
  color: var(--secondary-text);
}

/* FOOTER */
.site-footer {
  background: rgba(255, 255, 255, 0.98);
  border-top: 1px solid rgba(209, 213, 219, 0.9);
  padding: 40px 0 20px;
  margin-top: 40px;
}

.footer-grid {
  max-width: 1180px;
  margin: 0 auto;
  padding: 0 20px;
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: 40px;
}

.footer-logo {
  font-family: var(--font-heading);
  font-size: 20px;
  font-weight: 700;
  color: var(--primary-text);
}

.footer-text {
  margin-top: 12px;
  color: var(--secondary-text);
  font-size: 14px;
}

.footer-links {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.footer-links h4 {
  font-weight: 700;
  color: var(--primary-text);
  margin: 0 0 4px;
  font-size: 14px;
}

.footer-links a {
  color: var(--secondary-text);
  text-decoration: none;
  font-size: 14px;
  transition: color 0.18s ease;
}

.footer-links a:hover {
  color: var(--pastel-lilac);
}

/* RESPONSIVE */
@media (max-width: 1024px) {
  .trending-grid {
    grid-template-columns: repeat(3, 1fr);
  }

  .picks-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .footer-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 30px;
  }
}

@media (max-width: 768px) {
  .nav-links {
    display: none;
  }

  .welcome-headline {
    font-size: 28px;
  }

  .section-heading {
    font-size: 22px;
  }

  .trending {
    margin: 0;
    border-radius: 0;
  }

  .trending-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 18px;
  }

  .picks-grid {
    grid-template-columns: 1fr;
  }

  .footer-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .welcome-headline {
    font-size: 23px;
  }

  .welcome-tagline {
    font-size: 14px;
  }

  .trending-grid {
    grid-template-columns: 1fr;
  }

  .category-pills {
    gap: 8px;
  }

  .pill {
    padding: 8px 18px;
    font-size: 13px;
  }
}
</style>
