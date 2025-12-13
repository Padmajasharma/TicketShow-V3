<template>
  <div>
    <h2>Theatres</h2>
    <button @click="fetchTheatres">Refresh</button>
    <ul>
      <li v-for="t in theatres" :key="t.id">
        {{ t.id }} - {{ t.name }} ({{ t.place }}) capacity: {{ t.capacity }}
        <router-link :to="`/admin/theatres/${t.id}/seats`">Edit Seats</router-link>
      </li>
    </ul>
    <h3>Create Theatre</h3>
    <form @submit.prevent="createTheatre">
      <input v-model="form.name" placeholder="Name" />
      <input v-model="form.place" placeholder="Place" />
      <input v-model.number="form.capacity" placeholder="Capacity" />
      <button type="submit">Create</button>
    </form>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  data(){
    return { theatres: [], form: {name:'',place:'',capacity:150} }
  },
  created(){ this.fetchTheatres() },
  methods:{
    fetchTheatres(){ axios.get('/admin/theatres').then(r=> this.theatres = r.data.theatres).catch(e=>console.error(e)) },
    createTheatre(){ axios.post('/admin/theatres', this.form).then(()=>{this.fetchTheatres(); this.form={name:'',place:'',capacity:150}}).catch(e=>console.error(e)) }
  }
}
</script>
