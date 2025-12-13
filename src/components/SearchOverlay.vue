<template>
  <div v-if="modelValue" class="search-overlay" @click="$emit('update:modelValue', false)">
    <div class="search-modal" @click.stop>
      <div class="search-header">
        <input
          v-model="localQuery"
          type="text"
          placeholder="Search shows by name..."
          class="search-input"
          @keyup.enter="emitSelectFirst"
        />
        <button class="search-close" @click="$emit('update:modelValue', false)">✕</button>
      </div>

      <div v-if="localQuery.trim()" class="search-results">
        <div v-if="filtered.length > 0" class="results-list">
          <div
            v-for="item in filtered"
            :key="item.id"
            class="search-result-item"
            @click="onSelect(item)"
          >
            <img :src="resolveImage(item)" :alt="item.name" class="result-poster" />
            <div class="result-info">
              <h4 class="result-title">{{ item.name }}</h4>
              <p class="result-meta">{{ item.tags || 'Show' }}</p>
            </div>
          </div>
        </div>
        <div v-else class="no-results">
          <p>No shows found matching "{{ localQuery }}"</p>
        </div>
      </div>
      <div v-else class="search-hint">
        <p>Type to search for shows...</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SearchOverlay',
  props: {
    modelValue: { type: Boolean, required: true },
    items: { type: Array, default: () => [] }
  },
  emits: ['update:modelValue', 'select'],
  data() {
    return { localQuery: '' };
  },
  computed: {
    filtered() {
      const q = this.localQuery.trim().toLowerCase();
      if (!q) return this.items;
      return this.items.filter(i => (i.name || '').toLowerCase().includes(q) || (i.tags || '').toLowerCase().includes(q));
    }
  },
  methods: {
    resolveImage(item) {
      const url = item.image;
      if (url && /^https?:\/\//i.test(url)) return url;
      if (url) return `uploads/${encodeURIComponent(url)}`;
      return "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='80' height='120' viewBox='0 0 80 120'%3E%3Crect fill='%23374151' width='80' height='120'/%3E%3Ctext fill='%239ca3af' font-family='sans-serif' font-size='10' x='50%25' y='50%25' text-anchor='middle' dy='.3em'%3EShow%3C/text%3E%3C/svg%3E";
    },
    onSelect(item) {
      this.$emit('select', item);
      this.$emit('update:modelValue', false);
    },
    emitSelectFirst() {
      if (this.filtered.length > 0) this.onSelect(this.filtered[0]);
    }
  }
};
</script>

<style scoped>
.search-overlay { position: fixed; inset: 0; background: rgba(15, 23, 42, 0.45); backdrop-filter: blur(6px); display: flex; align-items: center; justify-content: center; z-index: 50; }
.search-modal { width: 680px; max-width: 92vw; background: #fff; border-radius: 18px; box-shadow: 0 20px 60px rgba(15, 23, 42, 0.35); padding: 16px; }
.search-header { display: flex; gap: 10px; align-items: center; }
.search-input { flex: 1; padding: 10px 14px; border: 1px solid #e5e7eb; border-radius: 10px; font-size: 15px; }
.search-close { border: none; background: #f1f5f9; padding: 8px 12px; border-radius: 10px; cursor: pointer; }
.results-list { display: grid; grid-template-columns: 1fr; gap: 10px; margin-top: 12px; max-height: 50vh; overflow: auto; }
.search-result-item { display: flex; gap: 12px; align-items: center; padding: 8px; border-radius: 12px; cursor: pointer; }
.search-result-item:hover { background: #f8fafc; }
.result-poster { width: 60px; height: 90px; border-radius: 8px; object-fit: cover; }
.result-info { flex: 1; }
.result-title { margin: 0; font-weight: 700; color: #0f172a; }
.result-meta { margin: 0; color: #6b7280; font-size: 13px; }
.search-hint, .no-results { padding: 20px; color: #6b7280; }
</style>
