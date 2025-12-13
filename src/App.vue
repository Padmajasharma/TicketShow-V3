<template>
  <div>
    <router-view></router-view>
  </div>
</template>

<script>
import TheatreList from './components/TheatreList.vue';
import ShowList from './components/ShowList.vue';

export default {
  // Add any necessary component logic here
  components: {
    TheatreList,
    ShowList,
  },
};
</script>
