<template>
  <div v-if="state.isOpen" style="position: fixed; inset: 0; background: rgba(15, 23, 42, 0.4); backdrop-filter: blur(6px); z-index: 9999; display: flex; align-items: center; justify-content: center; padding: 20px;">
    <div style="background: var(--bg-panel); border: 1px solid var(--border-color); width: 100%; max-width: 480px; border-radius: var(--border-radius); overflow: hidden; box-shadow: var(--shadow-premium); border-top: 4px solid var(--dialog-color);">
      <div style="padding: 16px 20px; border-bottom: 1px solid var(--border-color); background: var(--bg-surface); display: flex; align-items: center; gap: 12px;">
        <component :is="dialogIcon" :size="22" :style="{ color: 'var(--dialog-color)' }" />
        <span style="font-family: var(--font-mono); font-weight: 700; color: var(--text-primary); text-transform: uppercase; letter-spacing: 0.5px; font-size: 0.9rem;">
          {{ dialogTitle }}
        </span>
      </div>

      <div style="padding: 24px 20px; color: var(--text-secondary); line-height: 1.6; font-size: 0.95rem; white-space: pre-line;">
        {{ state.message }}
      </div>

      <div style="padding: 15px 20px; border-top: 1px solid var(--border-color); display: flex; gap: 15px; justify-content: flex-end; background: var(--bg-surface-hover);">
        <button v-if="state.isConfirm" class="btn btn-secondary" @click="closeDialog(false)">Annuler</button>
        <button class="btn btn-primary" :style="confirmBtnStyle" @click="closeDialog(true)">
          {{ state.isConfirm ? 'Confirmer' : 'Compris' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  AlertCircle as AlertCircleIcon,
  Info as InfoIcon,
  XCircle as XCircleIcon,
  CheckCircle2 as CheckCircleIcon
} from 'lucide-vue-next'
import { useAppDialog } from '~/composables/useAppDialog'

const { state, closeDialog } = useAppDialog()

const dialogIcon = computed(() => {
  if (state.value.type === 'error') return XCircleIcon
  if (state.value.type === 'success') return CheckCircleIcon
  if (state.value.type === 'warning') return AlertCircleIcon
  return InfoIcon
})

const dialogTitle = computed(() => {
  if (state.value.isConfirm) return 'Confirmation Requise'
  if (state.value.type === 'error') return 'Signalement / Erreur'
  if (state.value.type === 'success') return 'Opération Réussie'
  if (state.value.type === 'warning') return 'Attention / Alerte'
  return 'Message Système'
})

const confirmBtnStyle = computed(() => {
  if (state.value.type === 'error' || state.value.isConfirm) {
    return {
      backgroundColor: 'var(--danger)',
      borderColor: 'var(--danger)',
      color: 'white'
    }
  }
  if (state.value.type === 'success') {
    return {
      backgroundColor: 'var(--success)',
      borderColor: 'var(--success)',
      color: 'white'
    }
  }
  return {}
})
</script>

<style scoped>
div {
  --dialog-color: v-bind("state.type === 'error' ? 'var(--danger)' : state.type === 'success' ? 'var(--success)' : state.type === 'warning' ? 'var(--warning)' : 'var(--primary)'");
}
</style>
