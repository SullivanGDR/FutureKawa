<template>
  <div class="login-wrapper">
    <div class="grid-overlay"></div>

    <div class="login-card">
      <div class="card-header">
        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="logo-icon">
          <path d="M17 8h1a4 4 0 1 1 0 8h-1" />
          <path d="M3 8h14v9a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4Z" />
          <line x1="6" y1="2" x2="6" y2="4" />
          <line x1="10" y1="2" x2="10" y2="4" />
          <line x1="14" y1="2" x2="14" y2="4" />
        </svg>
        <h2 class="title">Future<span>Kawa</span></h2>
        <p class="subtitle font-mono">CONSOLE DE SUPERVISION INDUSTRIELLE</p>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="input-group">
          <label class="input-label font-mono">ADRESSE E-MAIL DE L'EMPLOYÉ</label>
          <input
            v-model="email"
            type="email"
            required
            placeholder="employe.bresil@futurekawa.com"
            class="industrial-input font-mono"
            :disabled="loading"
          />
        </div>

        <div class="input-group">
          <label class="input-label font-mono">MOT DE PASSE D'ACCÈS</label>
          <input
            v-model="password"
            type="password"
            required
            placeholder="••••••••"
            class="industrial-input font-mono"
            :disabled="loading"
          />
        </div>

        <div v-if="error" class="alert-box danger font-mono">
          <span class="alert-title">[ ACCÈS REFUSÉ ]</span>
          <span class="alert-message">{{ error }}</span>
        </div>

        <button type="submit" class="btn-login font-mono" :disabled="loading">
          <span v-if="loading">[ VALIDATION DU PROFIL... ]</span>
          <span v-else>SE CONNECTER</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

definePageMeta({
  layout: false
})

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref(null)

const { login } = useAuth()

const handleLogin = async () => {
  loading.value = true
  error.value = null
  try {
    await login(email.value, password.value)
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-wrapper {
  position: relative;
  min-height: 100vh;
  width: 100vw;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--bg-app);
  overflow: hidden;
  padding: 16px;
}

.grid-overlay {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(0, 0, 0, 0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 0, 0, 0.02) 1px, transparent 1px);
  background-size: 25px 25px;
  pointer-events: none;
  z-index: 1;
}

.login-card {
  position: relative;
  z-index: 2;
  width: 100%;
  max-width: 440px;
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-premium);
  overflow: hidden;
  padding: 0;
}

.card-status-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--bg-app);
  padding: 8px 16px;
  font-size: 0.65rem;
  color: var(--text-muted);
  border-bottom: 1px solid var(--border-color);
  font-weight: 600;
  letter-spacing: 0.5px;
}

.led-pulse {
  width: 6px;
  height: 6px;
  background-color: var(--success);
  border-radius: 50%;
  box-shadow: 0 0 8px var(--success);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { opacity: 0.4; }
  50% { opacity: 1; }
  100% { opacity: 0.4; }
}

.card-header {
  padding: 30px 30px 10px 30px;
  text-align: center;
}

.logo-icon {
  color: var(--primary);
  margin-bottom: 12px;
}

.title {
  font-family: var(--font-sans);
  font-size: 1.6rem;
  font-weight: 700;
  color: var(--text-primary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.title span {
  color: var(--text-muted);
  font-weight: 400;
}

.subtitle {
  font-size: 0.65rem;
  color: var(--text-muted);
  margin-top: 4px;
  font-weight: bold;
  letter-spacing: 1px;
}

.login-form {
  padding: 20px 30px 30px 30px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.input-label {
  font-size: 0.65rem;
  font-weight: 700;
  color: var(--text-secondary);
  letter-spacing: 0.5px;
}

.industrial-input {
  width: 100%;
  padding: 10px 12px;
  font-size: 0.85rem;
  background: var(--bg-app);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  border-radius: var(--border-radius);
  outline: none;
  transition: all 0.2s ease;
}

.industrial-input:focus {
  border-color: var(--border-color-active);
  background: var(--bg-surface);
}

.alert-box {
  padding: 10px 14px;
  border-radius: var(--border-radius);
  font-size: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.alert-box.danger {
  background: var(--danger-bg);
  border: 1px solid var(--danger);
  color: var(--danger);
}

.alert-title {
  font-weight: bold;
}

.btn-login {
  width: 100%;
  padding: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  background: var(--primary);
  color: var(--bg-surface);
  border: 1px solid var(--primary);
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-login:hover:not(:disabled) {
  background: var(--primary-hover);
  border-color: var(--primary-hover);
  box-shadow: var(--shadow-md);
}

.btn-login:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  background: var(--bg-app);
  padding: 10px 20px;
  font-size: 0.6rem;
  color: var(--text-muted);
  border-top: 1px solid var(--border-color);
  font-weight: 500;
}
</style>
