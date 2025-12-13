<template>
  <div>
    <h2>Seat Layout Editor - Theatre {{ theatreId }}</h2>
    <div>
      <input type="file" @change="onFile" />
      <button @click="exportCsv">Export CSV</button>
    </div>
    <table>
      <thead><tr><th>Row</th><th>Number</th><th>Type</th><th>Active</th></tr></thead>
      <tbody>
        <tr v-for="s in seats" :key="s.id">
          <td>{{ s.row_label }}</td>
          <td>{{ s.seat_number }}</td>
          <td>{{ s.seat_type }}</td>
          <td>{{ s.is_active ? 'Yes' : 'No' }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  data(){return { seats: [], file:null }},
  computed:{ theatreId(){ return this.$route.params.id } },
  created(){ this.fetchSeats() },
  methods:{
    fetchSeats(){ axios.get(`/theatres/${this.theatreId}/seats`).then(r=> this.seats = r.data.seats || r.data).catch(e=>console.error(e)) },
    onFile(e){ this.file = e.target.files[0]; this.upload() },
    upload(){ if(!this.file) return; const fd = new FormData(); fd.append('file', this.file); axios.post(`/admin/theatres/${this.theatreId}/seats/import`, fd, { headers: {'Content-Type':'multipart/form-data'} }).then(()=>{ this.fetchSeats() }).catch(e=>console.error(e)) },
    exportCsv(){ window.open(`/admin/theatres/${this.theatreId}/seats/export`, '_blank') }
  }
}
</script>

<style scoped>
table{width:100%;border-collapse:collapse}
th,td{border:1px solid #ddd;padding:8px}
</style>
