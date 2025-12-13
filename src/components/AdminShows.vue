<template>
  <div class="admin-shows">
    <h2>Shows</h2>
    <button @click="fetchShows">Refresh</button>
    <table>
      <thead>
        <tr><th>ID</th><th>Name</th><th>Theatre</th><th>Start</th><th>End</th></tr>
      </thead>
      <tbody>
        <tr v-for="s in shows" :key="s.id">
          <td>{{ s.id }}</td>
          <td>{{ s.name }}</td>
          <td>{{ s.theatre_id }}</td>
          <td>{{ s.start_time }}</td>
          <td>{{ s.end_time }}</td>
        </tr>
      </tbody>
    </table>
    <h3>Create Show</h3>
    <form @submit.prevent="createShow">
      <input v-model="form.name" placeholder="Name" />
      <input v-model="form.theatre_id" placeholder="Theatre ID" />
      <input v-model="form.start_time" placeholder="Start ISO" />
      <input v-model="form.end_time" placeholder="End ISO" />
      <input v-model="form.ticket_price" placeholder="Price" />
      <button type="submit">Create</button>
    </form>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  data(){
    return {
      shows: [],
      form: { name:'', theatre_id:'', start_time:'', end_time:'', ticket_price:0 }
    }
  },
  created(){ this.fetchShows() },
  methods: {
    fetchShows(){
      axios.get('/admin/shows')
        .then(r => { this.shows = r.data.shows })
        .catch(e=> console.error(e))
    },
    createShow(){
      axios.post('/admin/shows', this.form)
        .then(()=>{ this.fetchShows(); this.form={name:'',theatre_id:'',start_time:'',end_time:'',ticket_price:0} })
        .catch(e=> console.error(e))
    }
  }
}
</script>

<style scoped>
table{width:100%;border-collapse:collapse}
th,td{border:1px solid #ddd;padding:8px}
</style>
