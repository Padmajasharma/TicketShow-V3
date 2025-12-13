<template>
  <div class="admin-page">
    <AppHeader @toggle-search="() => {}" @go-profile="() => {}" />
    
    <div class="page-title-section">
      <div class="container">
        <div class="title-row">
          <div class="title-left">
            <h1 class="page-title">Manage Theatres</h1>
            <p class="page-subtitle">Add, edit, or remove theatre venues</p>
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
          <button @click="showForm = true" class="btn-primary">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
            Add Theatre
          </button>
        </div>

        <div class="card table-card">
          <table v-if="theatres.length > 0" class="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Place</th>
                <th>Capacity</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="theatre in theatres" :key="theatre.id">
                <td class="id-cell">{{ theatre.id }}</td>
                <td class="name-cell">{{ theatre.name }}</td>
                <td>{{ theatre.place }}</td>
                <td>{{ theatre.capacity }}</td>
                <td class="actions-cell">
                  <button class="action-btn edit" @click="editTheatre(theatre)">Edit</button>
                  <button class="action-btn delete" @click="deleteTheatre(theatre.id)">Delete</button>
                  <button class="action-btn export" @click="exportTheatreCSV(theatre.id)">Export</button>
                </td>
              </tr>
            </tbody>
          </table>
          <div v-else class="empty-state">
            <p>No theatres found. Add your first theatre!</p>
          </div>
        </div>

        <!-- Modal Form -->
        <div v-if="showForm" class="modal-overlay" @click.self="cancelForm">
          <div class="modal">
            <div class="modal-header">
              <h2>{{ editMode ? 'Edit Theatre' : 'Create Theatre' }}</h2>
              <button class="modal-close" @click="cancelForm">&times;</button>
            </div>
            <div class="modal-body">
              <input type="hidden" v-model="theatreData.id">
              <div class="form-group">
                <label>Name</label>
                <input type="text" v-model="theatreData.name" placeholder="Theatre name" required>
              </div>
              <div class="form-group">
                <label>Place</label>
                <input type="text" v-model="theatreData.place" placeholder="Location" required>
              </div>
              <div class="form-group">
                <label>Capacity</label>
                <input type="number" v-model="theatreData.capacity" placeholder="Seats" required>
              </div>
            </div>
            <div class="modal-footer">
              <button class="btn-cancel" @click="cancelForm">Cancel</button>
              <button class="btn-primary" @click="saveTheatre">{{ editMode ? 'Save Changes' : 'Create' }}</button>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>





<script>
import axios from 'axios';
import { jwtDecode } from 'jwt-decode';
import AppHeader from './AppHeader.vue';

export default {
  components: { AppHeader },
  data() {
    return {
      theatres: [],
      showForm: false,
      editMode: false,
      theatreData: {
        id: null,
        name: '',
        place: '',
        capacity: null,
      },
      message: '',
    };
  },
  props: ['theatre'],
  
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
    fetchTheatres() {

  const token = localStorage.getItem('access_token');


  if (!token) {
    console.error('Unauthorized: JWT token not found');
    return;
  }

  const headers = {  
    Authorization: `Bearer ${token}`,
  };

  axios.get('theatres', { headers } ,console.log('request sent'))
    .then(response => {
      this.theatres = response.data;

     
      this.showForm = false;
    })
    .catch(error => {
      console.error('Error fetching theatres:', error);
    });
},



editTheatre(theatre) {
  if (theatre) {
    this.theatreData.id = theatre.id;
    this.theatreData.name = theatre.name;
    this.theatreData.place = theatre.place;
    this.theatreData.capacity = theatre.capacity;
    this.editMode = true;
    this.showForm = true;
  } 
},

    cancelForm() {
      this.showForm = false;
      this.editMode = false; 
    },

    saveTheatre() {
   
    const token = localStorage.getItem('access_token');

    if (!token) {
      console.error('Unauthorized: JWT token not found');
      return;
    }

    const headers = { 
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    };

    if (this.editMode) {
      const theatreId = this.theatreData.id;
      axios
        .put(`theatres/${theatreId}`, this.theatreData, { headers })
        .then(response => {
          this.message = response.data.message;

         
          const index = this.theatres.findIndex(theatre => theatre.id === this.theatreData.id);
          if (index !== -1) {
            this.theatres[index] = { ...this.theatreData };
          }

        
          this.showForm = false;
          this.editMode = false;

          
          this.fetchTheatres();

          
        })
        .catch(error => {
          console.error('Error updating theatre:', error);
        });
    } else {
     
      axios
        .post('theatres', this.theatreData, { headers })
        .then(response => {
          // Backend returns the theatre object directly
          this.theatres.push(response.data);
          this.message = 'Theatre created successfully!';

          
          this.showForm = false;
          this.theatreData.name = '';
          this.theatreData.place = '';
          this.theatreData.capacity = null;
          this.editMode = false; 
        
          this.fetchTheatres();

          
        })
        .catch(error => {
          console.error('Error creating theatre:', error);
        });
    }
  },

  deleteTheatre(theatreId) {
  
  const token = localStorage.getItem('access_token');


  if (!token) {
    console.error('Unauthorized: JWT token not found');
    return;
  }


  const headers = {
    Authorization: `Bearer ${token}`,
  };

 
  axios
    .delete(`theatres/${theatreId}`, { headers })
    .then(response => {
      this.message = response.data.message;

      this.theatres = this.theatres.filter(theatre => theatre.id !== theatreId);


    })
    .catch(error => {
      console.error('Error deleting theatre:', error);
    });
},
logout() {
      
      localStorage.removeItem('access_token');
      this.$router.push('/');
    },
    goToDashboard() {
   
      this.$router.push('/adminDashboard');
    },
    
    exportTheatreCSV(theatreId) {
      const token = localStorage.getItem('access_token');

      if (!token) {
        console.error('Unauthorized: JWT token not found');
        return;
      }

      const headers = {
        Authorization: `Bearer ${token}`,
      };

      axios.get(`export_theatre/${theatreId}`, { headers })
        .then(response => {
          if (response.data.status === 'success') {
            // Decode base64 data
            const csvData = atob(response.data.data);
            const blob = new Blob([csvData], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            
            // Create download link
            const link = document.createElement('a');
            link.href = url;
            link.download = response.data.filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(url);
            
            this.message = 'Export successful!';
          } else {
            console.error('Export failed:', response.data.message);
            this.message = 'Export failed: ' + response.data.message;
          }
        })
        .catch(error => {
          console.error('Error triggering export task:', error);
          this.message = 'Export failed. Make sure Redis and Celery are running.';
        });
    }


  
}, 
  
mounted() {
    this.fetchTheatres();
  },

}

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
  max-width: 1100px;
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
  padding: 14px 16px;
  text-align: left;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #6b7280;
  border-bottom: 1px solid rgba(168, 85, 247, 0.1);
}

.data-table td {
  padding: 16px;
  border-bottom: 1px solid rgba(168, 85, 247, 0.05);
  color: #0f172a;
}

.data-table tr:last-child td {
  border-bottom: none;
}

.data-table tr:hover {
  background: rgba(168, 85, 247, 0.02);
}

.id-cell {
  font-weight: 600;
  color: #a855f7;
}

.name-cell {
  font-weight: 600;
}

.actions-cell {
  display: flex;
  gap: 8px;
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

.action-btn.export {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.action-btn.export:hover {
  background: #3b82f6;
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
  max-width: 480px;
  margin: 20px;
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
</style>
