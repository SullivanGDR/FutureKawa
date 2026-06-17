<template>
  <div class="pagination-container" v-if="totalPages > 1">
    <div class="pagination-info">
      Affichage {{ startIndex + 1 }} à {{ Math.min(endIndex, totalItems) }} sur {{ totalItems }} enregistrements
    </div>

    <div class="pagination-controls">
      <button
        class="pagination-btn"
        :disabled="currentPage === 1"
        @click="goToPage(currentPage - 1)"
      >
        <component :is="ChevronLeftIcon" :size="16" />
      </button>

      <div class="pagination-numbers">
        <button
          v-for="page in visiblePages"
          :key="page"
          class="pagination-number"
          :class="{ active: page === currentPage }"
          @click="page !== '...' ? goToPage(page) : null"
          :disabled="page === '...'"
        >
          {{ page }}
        </button>
      </div>

      <button
        class="pagination-btn"
        :disabled="currentPage === totalPages"
        @click="goToPage(currentPage + 1)"
      >
        <component :is="ChevronRightIcon" :size="16" />
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { ChevronLeft as ChevronLeftIcon, ChevronRight as ChevronRightIcon } from 'lucide-vue-next'

const props = defineProps({
  modelValue: {
    type: Number,
    required: true
  },
  totalItems: {
    type: Number,
    required: true
  },
  itemsPerPage: {
    type: Number,
    default: 10
  }
})

const emit = defineEmits(['update:modelValue'])

const currentPage = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const totalPages = computed(() => Math.max(1, Math.ceil(props.totalItems / props.itemsPerPage)))

const startIndex = computed(() => (currentPage.value - 1) * props.itemsPerPage)
const endIndex = computed(() => startIndex.value + props.itemsPerPage)

const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

const visiblePages = computed(() => {
  const current = currentPage.value
  const last = totalPages.value

  if (last <= 7) {
    return Array.from({ length: last }, (_, i) => i + 1)
  }

  if (current <= 4) {
    return [1, 2, 3, 4, 5, '...', last]
  }

  if (current >= last - 3) {
    return [1, '...', last - 4, last - 3, last - 2, last - 1, last]
  }

  return [1, '...', current - 1, current, current + 1, '...', last]
})
</script>

<style scoped>
.pagination-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background-color: var(--bg-surface);
  border-top: 1px solid var(--border-color);
  font-family: var(--font-sans);
}

.pagination-info {
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pagination-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: var(--border-radius);
  background-color: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.2s;
}

.pagination-btn:hover:not(:disabled) {
  background-color: var(--bg-surface-hover);
  border-color: var(--border-color-active);
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  color: var(--text-muted);
}

.pagination-numbers {
  display: flex;
  gap: 4px;
}

.pagination-number {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  height: 32px;
  padding: 0 8px;
  border-radius: var(--border-radius);
  background-color: transparent;
  border: 1px solid transparent;
  color: var(--text-secondary);
  font-size: 0.85rem;
  font-family: var(--font-mono);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.pagination-number:hover:not(:disabled) {
  color: var(--text-primary);
  background-color: var(--bg-surface-hover);
}

.pagination-number.active {
  background-color: var(--border-color-active);
  color: var(--text-primary);
  border-color: var(--border-color-active);
}

.pagination-number:disabled {
  cursor: default;
  color: var(--text-muted);
}
</style>
