<template>
  <div class="admin-page">
    <AppHeader @toggle-search="() => {}" @go-profile="() => {}" />
    
    <div class="page-title-section">
      <div class="container">
        <div class="title-row">
          <div class="title-left">
            <h1 class="page-title">Manage Shows</h1>
            <p class="page-subtitle">Schedule and update show listings</p>
          </div>
          <button @click="goToDashboard" class="btn-secondary">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="m15 18-6-6 6-6"></path>
            </svg>
            Dashboard
          </button>
        </div>
      </div>
    </div>

    <main class="page-main">
      <div class="container">
        <div v-if="message" class="message-banner">{{ message }}</div>

        <div class="toolbar">
          <button @click="showForm=true" class="btn-primary">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
            Add Show
          </button>
        </div>

        <div class="card table-card">
          <table v-if="shows.length > 0" class="data-table">
            <thead>
              <tr>
                <th>Poster</th>
                <th>Name</th>
                <th>Rating</th>
                <th>Tags</th>
                <th>Price</th>
                <th>Start</th>
                <th>End</th>
                <th>Theatre</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="show in shows" :key="show.id">
                <td class="poster-cell">
                  <img 
                    v-if="show.image" 
                    :src="show.image" 
                    :alt="show.name" 
                    class="table-poster"
                    @error="$event.target.src = placeholder"
                  />
                  <div v-else class="no-poster">No Image</div>
                </td>
                <td class="name-cell">{{ show.name }}</td>
                <td><span class="rating-badge">★ {{ show.rating || 0 }}</span></td>
                <td><span class="tag-badge">{{ show.tags }}</span></td>
                <td>₹{{ show.ticket_price }}</td>
                <td class="time-cell">{{ formatTimeSimple(show.start_time) }}</td>
                <td class="time-cell">{{ formatTimeSimple(show.end_time) }}</td>
                <td>{{ getTheatreName(show.theatre_id) }}</td>
                <td class="actions-cell">
                  <button class="action-btn edit" @click="editShow(show)">Edit</button>
                  <button class="action-btn delete" @click="confirmDelete(show)">Delete</button>
                </td>
              </tr>
            </tbody>
          </table>
          <div v-else class="empty-state">
            <p>No shows found. Add your first show!</p>
          </div>
        </div>

        <!-- Modal Form -->
        <div v-if="showForm" class="modal-overlay" @click.self="cancelForm">
          <div class="modal">
            <div class="modal-header">
              <h2>{{ editMode ? 'Edit Show' : 'Create Show' }}</h2>
              <button class="modal-close" @click="cancelForm">&times;</button>
            </div>
            <div class="modal-body">
              <div class="form-group">
                <label>Name</label>
                <input type="text" v-model="showData.name" placeholder="Show name" required>
              </div>
              
              <!-- Show Type Selector -->
              <div class="form-group">
                <label>Type</label>
                <select v-model="showData.show_type" class="type-select">
                  <option value="movie">🎬 Movie</option>
                  <option value="concert">🎤 Concert</option>
                  <option value="play">🎭 Play</option>
                  <option value="event">🎪 Event</option>
                </select>
              </div>
              
              <!-- TMDB for Movies -->
              <div v-if="showData.show_type === 'movie'" class="form-group">
                <label>TMDB ID (auto-fetch poster)</label>
                <div class="tmdb-input-group">
                  <input type="text" v-model="showData.tmdb_id" placeholder="Enter TMDB movie ID" @blur="fetchTMDBPoster">
                  <button type="button" class="btn-fetch" @click="fetchTMDBPoster" :disabled="fetchingPoster">
                    {{ fetchingPoster ? 'Fetching...' : 'Fetch' }}
                  </button>
                </div>
                <small class="help-text">Find ID from themoviedb.org (e.g., /movie/550 → ID is 550)</small>
              </div>
              
              <!-- Manual Image URL for Concerts/Plays/Events -->
              <div v-else class="form-group">
                <label>Image URL</label>
                <input type="text" v-model="showData.image" placeholder="Paste image URL (poster, artist photo, etc.)">
                <small class="help-text">Paste a direct image link or upload to imgur.com first</small>
              </div>
              
              <div v-if="posterPreview || showData.image" class="poster-preview">
                <img :src="posterPreview || showData.image" alt="Poster preview" @error="handleImageError" />
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label>Tags</label>
                  <input type="text" v-model="showData.tags" placeholder="e.g., Action, Drama, Rock, Comedy" required>
                </div>
                <div class="form-group">
                  <label>Ticket Price</label>
                  <input type="number" v-model="showData.ticket_price" placeholder="₹" required>
                </div>
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label>Date</label>
                  <input type="date" v-model="showData.date" required>
                </div>
                <div class="form-group">
                  <label>Start Time</label>
                  <input type="time" v-model="showData.start_time_only" required>
                </div>
                <div class="form-group">
                  <label>End Time</label>
                  <input type="time" v-model="showData.end_time_only" required>
                </div>
              </div>
              <div class="form-group">
                <label>Theatre</label>
                <select v-model="showData.theatre_id" required>
                  <option v-for="theatre in theatres" :key="theatre.id" :value="theatre.id">{{ theatre.name }}</option>
                </select>
              </div>
            </div>
            <div class="modal-footer">
              <button class="btn-cancel" @click="cancelForm">Cancel</button>
              <button class="btn-primary" @click="saveShow">{{ editMode ? 'Save Changes' : 'Create' }}</button>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import axios from 'axios';
import { jwtDecode } from "jwt-decode";
import AppHeader from './AppHeader.vue';

export default {
  components: { AppHeader },
  data() {
    return {
      shows: [],
      theatres: [], 
      showForm: false,
      editMode: false,
      fetchingPoster: false,
      posterPreview: null,
      placeholder: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='60' height='90' viewBox='0 0 60 90'%3E%3Crect fill='%23374151' width='60' height='90'/%3E%3Ctext fill='%239ca3af' font-family='sans-serif' font-size='8' x='50%25' y='50%25' text-anchor='middle' dy='.3em'%3ENo Image%3C/text%3E%3C/svg%3E",
      TMDB_API_KEY: '9f044f29dce2ab2f0084689d8a610547', // Your TMDB API key
      showData: {
        id: null,
        name: '',
        show_type: 'movie', // movie, concert, play, event
        tmdb_id: '',
        date: '',
        start_time_only: '',
        end_time_only: '',
        tags: '',
        ticket_price: null,
        theatre_id: null,
        image: null,
        // TMDB metadata
        overview: '',
        runtime: null,
        release_date: '',
        tmdb_rating: null,
        backdrop: '',
      },
      message: '',

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
},
  methods: {
    // Image helpers (not currently used in this admin table, but kept for consistency)
    localAssetFor(name) {
      const key = (name || '').toLowerCase();
      const map = {
        'arijit singh': require('@/assets/arijit.jpeg'),
        'tyla': require('@/assets/Tyla.jpg'),
        'hamlet': require('@/assets/Hamlet.jpg')
      };
      if (map[key]) return map[key];
      if (key.includes('arijit')) return require('@/assets/arijit.jpeg');
      if (key.includes('tyla')) return require('@/assets/Tyla.jpg');
      if (key.includes('hamlet')) return require('@/assets/Hamlet.jpg');
      return null;
    },
    tmdbPosterFor(name) {
      const key = (name || '').toLowerCase();
      const posters = {
        'fight club': 'https://image.tmdb.org/t/p/w500/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg',
        'the shawshank redemption': 'https://image.tmdb.org/t/p/w500/9cqNxx0GxF0bflZmeSMuL5tnGzr.jpg',
        'the godfather': 'https://image.tmdb.org/t/p/w500/e5iVtjkjM30znn86JsvkBYtvEo1.jpg',
        'the godfather: part ii': 'https://image.tmdb.org/t/p/w500/hek3koDUyRQk7FIhPXsa6mT2Zc3.jpg',
        "schindler's list": 'https://image.tmdb.org/t/p/w500/sF1U4EUQS8YHUYjNl3pMGNIQyr0.jpg',
        '12 angry men': 'https://image.tmdb.org/t/p/w500/ow3wq89wM8qd5X7hWKxiRfsFf9C.jpg'
      };
      return posters[key] || null;
    },
    resolvedImage(url, name) {
      const local = this.localAssetFor(name);
      if (local) return local;
      if (url && typeof url === 'string' && /^https?:\/\//.test(url)) return url;
      const tmdb = this.tmdbPosterFor(name);
      if (tmdb) return tmdb;
      if (url && typeof url === 'string' && url.length > 0) return `uploads/${url}`;
      return "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='450' viewBox='0 0 300 450'%3E%3Crect fill='%23374151' width='300' height='450'/%3E%3Ctext fill='%239ca3af' font-family='sans-serif' font-size='16' x='50%25' y='50%25' text-anchor='middle' dy='.3em'%3EShow%3C/text%3E%3C/svg%3E";
    },
   
    fetchShows() {
      const token = localStorage.getItem('access_token');
  if (!token) {
    console.error('Unauthorized: JWT token not found');
    return;
  }

  const headers = {
    Authorization: `Bearer ${token}`,
  };
      axios.get('shows',{headers})
        .then(response => {
          this.shows = response.data;
          this.showForm = false;
        })
        .catch(error => {
          console.error('Error fetching shows:', error);
        });
    },

    fetchTheatres() {
 
  const token = localStorage.getItem('access_token');


  if (!token) {
    console.error('Unauthorized: JWT token not found');
    return;
  }

 
  const headers = { 
    Authorization: `Bearer ${token}`,
  };

  axios.get('theatres', { headers })
    .then(response => {
      this.theatres = response.data;

      
      this.showForm = false;
    })
    .catch(error => {
      console.error('Error fetching theatres:', error);
    });
},

    async fetchTMDBPoster() {
      if (!this.showData.tmdb_id) return;
      
      this.fetchingPoster = true;
      try {
        // Try movie first
        let response = await fetch(
          `https://api.themoviedb.org/3/movie/${this.showData.tmdb_id}?api_key=${this.TMDB_API_KEY}`
        );
        let data = await response.json();
        
        // If not found as movie, try TV show
        if (data.success === false) {
          response = await fetch(
            `https://api.themoviedb.org/3/tv/${this.showData.tmdb_id}?api_key=${this.TMDB_API_KEY}`
          );
          data = await response.json();
        }
        
        if (data.poster_path) {
          const posterUrl = `https://image.tmdb.org/t/p/w500${data.poster_path}`;
          this.showData.image = posterUrl;
          this.posterPreview = posterUrl;
          
          // Auto-fill name if empty
          if (!this.showData.name) {
            this.showData.name = data.title || data.name || '';
          }
          
          // Store additional TMDB metadata
          this.showData.overview = data.overview || '';
          this.showData.runtime = data.runtime || null;
          this.showData.release_date = data.release_date || data.first_air_date || '';
          this.showData.tmdb_rating = data.vote_average || null;
          
          // Store backdrop
          if (data.backdrop_path) {
            this.showData.backdrop = `https://image.tmdb.org/t/p/w1280${data.backdrop_path}`;
          }
          
          // Auto-fill tags from genres if empty
          if (!this.showData.tags && data.genres && data.genres.length > 0) {
            this.showData.tags = data.genres.map(g => g.name).join(', ');
          }
          
          this.message = 'TMDB data fetched successfully!';
        } else {
          this.message = 'No poster found for this TMDB ID';
        }
      } catch (error) {
        console.error('Error fetching TMDB data:', error);
        this.message = 'Failed to fetch from TMDB';
      } finally {
        this.fetchingPoster = false;
      }
    },

    formatTimeSimple(isoString) {
      if (!isoString) return '';
      const date = new Date(isoString);
      return date.toLocaleString('en-IN', {
        day: 'numeric',
        month: 'short',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
      });
    },

    getTheatreName(theatreId) {
      const theatre = this.theatres.find(t => t.id === theatreId);
      return theatre ? theatre.name : `Theatre #${theatreId}`;
    },

    createShow() {
      
      this.showData.id = null;
      this.showData.name = '';
      this.showData.show_type = 'movie';
      this.showData.tmdb_id = '';
      this.showData.image = null;
      this.showData.date = '';
      this.showData.start_time_only = '';
      this.showData.end_time_only = '';
      this.showData.start_time = null;
      this.showData.end_time = null;
      this.showData.tags = '';
      this.showData.ticket_price = null;
      this.showData.theatre_id = null;
      this.showData.overview = '';
      this.showData.runtime = null;
      this.showData.release_date = '';
      this.showData.tmdb_rating = null;
      this.showData.backdrop = '';
      this.posterPreview = null;

      this.editMode = false;
      this.showForm = true;
    },

    editShow(show) {
      
      this.showData.id = show.id;
      this.showData.name = show.name;
      this.showData.start_time = show.start_time;
      this.showData.end_time = show.end_time; 
      this.showData.rating = show.rating;
      this.showData.tags = show.tags;
      this.showData.ticket_price = show.ticket_price;
      this.showData.theatre_id = show.theatre_id;
      this.showData.image = show.image;
      this.posterPreview = show.image; // Show existing poster

      this.editMode = true;
      this.showForm = true;
    },
    async saveShow() {
  const token = localStorage.getItem('access_token');

 
  if (!token) {
    console.error('Unauthorized: JWT token not found');
    return;
  }


  const headers = { 
    Authorization: `Bearer ${token}`,
  };

  if (this.editMode) {
  
    this.showData.start_time = this.formatDate(this.showData.start_time);
    this.showData.end_time = this.formatDate(this.showData.end_time);

    console.log('Formatted Start Time2:', this.showData.start_time);
console.log('Formatted End Time2:', this.showData.end_time);
    console.log(this.showData);
    axios.put(`shows/${this.showData.id}`, this.showData, { headers })
      .then(response => {
        this.message = response.data.message;

   
        this.showForm = false;
        this.editMode = false;

      
        this.fetchShows();

   
      })
      .catch(error => {
        console.error('Error updating show:', error);
      });
  } 
  
  else {
    try {
  // Combine date and time fields for new shows
  const startDateTime = `${this.showData.date}T${this.showData.start_time_only}`;
  const endDateTime = `${this.showData.date}T${this.showData.end_time_only}`;
  
  // Use JSON body with TMDB poster URL instead of FormData
  const showPayload = {
    name: this.showData.name,
    start_time: startDateTime,
    end_time: endDateTime,
    tags: this.showData.tags,
    ticket_price: this.showData.ticket_price,
    theatre_id: this.showData.theatre_id,
    image: this.showData.image || '', // TMDB poster URL
    // TMDB metadata
    tmdb_id: this.showData.tmdb_id ? parseInt(this.showData.tmdb_id) : null,
    overview: this.showData.overview || '',
    runtime: this.showData.runtime,
    release_date: this.showData.release_date || '',
    tmdb_rating: this.showData.tmdb_rating,
    backdrop: this.showData.backdrop || '',
  };

  const headers = {
    Authorization: `Bearer ${token}`,
    'Content-Type': 'application/json',
  };

  const response = await axios.post('shows', showPayload, { headers });
  console.log(response.data);

  this.message = response.data.message;
  this.showForm = false;
  // Reset all fields
  this.showData.name = '';
  this.showData.tmdb_id = '';
  this.showData.date = '';
  this.showData.start_time_only = '';
  this.showData.end_time_only = '';
  this.showData.start_time = null;
  this.showData.end_time = null;
  this.showData.tags = '';
  this.showData.ticket_price = null;
  this.showData.theatre_id = null;
  this.showData.image = null;
  this.showData.overview = '';
  this.showData.runtime = null;
  this.showData.release_date = '';
  this.showData.tmdb_rating = null;
  this.showData.backdrop = '';
  this.posterPreview = null;
  this.editMode = false;

  this.fetchShows();
} catch (error) {
  // Handle the error here, you can log it or show an error message to the user
  console.error('An error occurred:', error);
  // Optionally, show an error message to the user
  this.message = 'An error occurred while saving the data.';
}
  }
},
    // New code for creating a show with image as JSON

    /* const imageFile = this.showData.image; // Access the image data from showData

    if (!imageFile) {
      console.error('Image file is required');
      return;
    }

    const base64ImageData = await this.readFileAsBase64(imageFile);

    const jsonData = {
      name: this.showData.name,
      start_time: this.formatDate(this.showData.start_time),
      end_time: this.formatDate(this.showData.end_time),
      tags: this.showData.tags,
      ticket_price: this.showData.ticket_price,
      theatre_id: this.showData.theatre_id,
      image: base64ImageData, // Include the base64-encoded image data
    };

    try {
      const response = await axios.post('shows', jsonData, { headers });

      console.log(response.data);
      this.message = response.data.message;
      this.showForm = false;

      this.fetchShows();
      // Reset your form data and other fields
    } catch (error) {
      console.error('An error occurred:', error);
      // Handle the error appropriately
      // Optionally, show an error message to the user
      this.message = 'An error occurred while saving the data.';
    }
  }
},

async readFileAsBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result.split(',')[1]); // Extract the base64 part
    reader.onerror = reject;
    reader.readAsDataURL(file); // Convert the image to base64
  });
},

  */


formatDate(dateString) {
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    
    const formattedDate = `${year}-${month}-${day}T${hours}:${minutes}`;
    return formattedDate;
},


    deleteShow(showId) {
      // Get the JWT token from localStorage
      const token = localStorage.getItem('access_token');

    
      if (!token) {
        console.error('Unauthorized: JWT token not found');
        return;
      }


      const headers = { 
        Authorization: `Bearer ${token}`,
      };

     
      axios
        .delete(`shows/${showId}`, { headers })
        .then(response => {
          this.message = response.data.message;

        
          this.shows = this.shows.filter(show => show.id !== showId);

        })
        .catch(error => {
          console.error('Error deleting show:', error);
        });
    },

    confirmDelete(show) {
      if (confirm('Are you sure you want to delete this show?')) {
        this.deleteShow(show.id);
      }
    },
    cancelForm() {
      this.showForm = false;
      this.editMode = false;
      this.posterPreview = null;
      this.showData.tmdb_id = '';
      this.showData.show_type = 'movie';
    },
    handleImageError(e) {
      e.target.style.display = 'none';
    },
    logout() {
      localStorage.removeItem('access_token');
      this.$router.push('/');
    },
    onFileChange(event) {
  const file = event.target.files[0];
  console.log('Selected file:', file);
  this.showData.image = file;
},

goToDashboard() {
   
   this.$router.push('/adminDashboard');
 },

    
  },

  

  mounted() {
    this.fetchShows();
    this.fetchTheatres();
  },
};
</script>


<style scoped>
.admin-page {
  min-height: 100vh;
  background:
    radial-gradient(circle at 0% 0%, rgba(217, 212, 241, 0.9) 0, transparent 55%),
    radial-gradient(circle at 100% 0%, rgba(250, 220, 217, 0.9) 0, transparent 55%),
    radial-gradient(circle at 0% 100%, rgba(215, 234, 248, 0.9) 0, transparent 55%),
    #f9fafb;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.page-title-section {
  padding: 30px 0 20px;
}

.title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
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

.btn-primary, .btn-secondary, .btn-logout, .btn-cancel {
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

.btn-primary {
  background: linear-gradient(135deg, #a855f7 0%, #ec4899 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(168, 85, 247, 0.3);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.9);
  color: #0f172a;
  border: 1px solid rgba(168, 85, 247, 0.2);
}

.btn-secondary:hover {
  border-color: #a855f7;
}

.btn-logout {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.btn-logout:hover {
  background: #ef4444;
  color: white;
}

.btn-cancel {
  background: #f1f5f9;
  color: #64748b;
}

.page-main {
  padding: 30px 0;
}

.message-banner {
  padding: 14px 20px;
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid rgba(34, 197, 94, 0.2);
  border-radius: 12px;
  color: #16a34a;
  font-weight: 500;
  margin-bottom: 20px;
}

.toolbar {
  margin-bottom: 20px;
}

.card {
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(168, 85, 247, 0.1);
  border-radius: 16px;
  overflow: hidden;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  background: rgba(168, 85, 247, 0.05);
  padding: 14px 12px;
  text-align: left;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #6b7280;
  border-bottom: 1px solid rgba(168, 85, 247, 0.1);
}

.data-table td {
  padding: 14px 12px;
  border-bottom: 1px solid rgba(168, 85, 247, 0.05);
  color: #0f172a;
  font-size: 14px;
}

.data-table tr:last-child td {
  border-bottom: none;
}

.data-table tr:hover {
  background: rgba(168, 85, 247, 0.02);
}

.name-cell {
  font-weight: 600;
}

.poster-cell {
  width: 60px;
  padding: 8px 12px;
}

.table-poster {
  width: 50px;
  height: 75px;
  object-fit: cover;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.no-poster {
  width: 50px;
  height: 75px;
  background: #f1f5f9;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  color: #9ca3af;
  text-align: center;
}

.time-cell {
  font-size: 12px;
  color: #6b7280;
}

.rating-badge {
  display: inline-block;
  padding: 4px 8px;
  background: rgba(251, 191, 36, 0.1);
  color: #d97706;
  font-size: 12px;
  font-weight: 600;
  border-radius: 6px;
}

.tag-badge {
  display: inline-block;
  padding: 4px 8px;
  background: rgba(168, 85, 247, 0.1);
  color: #a855f7;
  font-size: 12px;
  border-radius: 6px;
}

.actions-cell {
  display: flex;
  gap: 6px;
}

.action-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn.edit {
  background: rgba(168, 85, 247, 0.1);
  color: #a855f7;
}

.action-btn.edit:hover {
  background: #a855f7;
  color: white;
}

.action-btn.delete {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.action-btn.delete:hover {
  background: #ef4444;
  color: white;
}

.empty-state {
  padding: 60px 20px;
  text-align: center;
  color: #6b7280;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  backdrop-filter: blur(4px);
}

.modal {
  background: white;
  border-radius: 20px;
  width: 100%;
  max-width: 560px;
  margin: 20px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px 24px 0;
}

.modal-header h2 {
  font-size: 20px;
  font-weight: 700;
  margin: 0;
  color: #0f172a;
}

.modal-close {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f1f5f9;
  border: none;
  border-radius: 8px;
  font-size: 20px;
  color: #64748b;
  cursor: pointer;
}

.modal-body {
  padding: 24px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 6px;
}

.form-group input, .form-group select {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  font-size: 14px;
  transition: all 0.2s ease;
}

.form-group input:focus, .form-group select:focus {
  outline: none;
  border-color: #a855f7;
  box-shadow: 0 0 0 3px rgba(168, 85, 247, 0.1);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 0 24px 24px;
}

/* TMDB input styling */
.tmdb-input-group {
  display: flex;
  gap: 10px;
}

.tmdb-input-group input {
  flex: 1;
}

.btn-fetch {
  padding: 10px 16px;
  background: linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.btn-fetch:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.btn-fetch:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.help-text {
  display: block;
  margin-top: 6px;
  font-size: 12px;
  color: #9ca3af;
}

.type-select {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  font-size: 14px;
}

.poster-preview {
  margin-bottom: 16px;
  text-align: center;
}

.poster-preview img {
  max-width: 200px;
  max-height: 300px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}
</style>