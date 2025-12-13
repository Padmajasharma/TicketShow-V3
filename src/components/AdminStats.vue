<template>
  <div>
    <h2>Admin Stats</h2>
    <div>
      <label>Since days: <input v-model.number="since" /></label>
      <button @click="fetchStats">Refresh</button>
    </div>
    <div>
      <h3>Totals</h3>
      <p>Bookings: {{ stats.total_bookings }}</p>
      <p>Revenue: {{ stats.total_revenue }}</p>
    </div>
    <div>
      <h3>Top Shows</h3>
      <ul>
        <li v-for="s in stats.top_shows" :key="s.show_id">{{ s.name }} - {{ s.bookings }}</li>
      </ul>
    </div>
    <div>
      <h3>Bookings Time Series</h3>
      <button @click="fetchTimeseries">Load Timeseries</button>
      <table>
        <thead><tr><th>Day</th><th>Bookings</th><th>Revenue</th></tr></thead>
        <tbody>
          <tr v-for="t in timeseries" :key="t.day">
            <td>{{ t.day }}</td>
            <td>{{ t.bookings }}</td>
            <td>{{ t.revenue }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  data(){ return { since:30, stats: {}, timeseries: [] } },
  created(){ this.fetchStats() },
  methods:{
    fetchStats(){ axios.get(`/admin/stats?since_days=${this.since}`).then(r=> this.stats = r.data).catch(e=>console.error(e)) },
    fetchTimeseries(){ axios.get(`/admin/stats/timeseries?since_days=${this.since}`).then(r=> this.timeseries = r.data.timeseries).catch(e=>console.error(e)) }
  }
}
</script>
