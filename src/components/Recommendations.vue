<template>
  <div>
    <h2>Recommendations</h2>
    <button @click="fetch">Refresh</button>
    <ul>
      <li v-for="r in recs" :key="r.id">{{ r.name }} ({{ r.bookings }} bookings)</li>
    </ul>
  </div>
</template>
<script>
import axios from 'axios'
export default {
  data(){ return { recs: [] } },
  created(){ this.fetch() },
  methods:{ fetch(){ axios.get('/recommendations').then(r=> this.recs = r.data.recommendations).catch(e=>console.error(e)) } }
}
</script>