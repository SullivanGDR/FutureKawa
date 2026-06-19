<template>
  <div class="app-container">
    <aside class="sidebar">
      <div class="sidebar-header">
        <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: var(--text-primary); flex-shrink: 0;">
          <path d="M17 8h1a4 4 0 1 1 0 8h-1" />
          <path d="M3 8h14v9a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4Z" />
          <line x1="6" y1="2" x2="6" y2="4" />
          <line x1="10" y1="2" x2="10" y2="4" />
          <line x1="14" y1="2" x2="14" y2="4" />
        </svg>
        <div>
          <h1 class="logo-text">Future<span>Kawa</span></h1>
          <span style="font-size: 0.65rem; color: var(--text-muted); font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase;">Console de Supervision</span>
        </div>
      </div>

      <nav class="sidebar-nav">
        <NuxtLink to="/" class="nav-item">
          <component :is="LayoutDashboardIcon" :size="18" />
          <span>Tableau de bord</span>
        </NuxtLink>
        <NuxtLink to="/lots" class="nav-item">
          <component :is="ContainerIcon" :size="18" />
          <span>Gestion des lots</span>
        </NuxtLink>
        <NuxtLink to="/parc" class="nav-item">
          <component :is="FactoryIcon" :size="18" />
          <span>Entrepôts</span>
        </NuxtLink>
        <NuxtLink to="/modules" class="nav-item">
          <component :is="CpuIcon" :size="18" />
          <span>Modules IoT</span>
        </NuxtLink>
        <NuxtLink to="/alertes" class="nav-item">
          <component :is="AlertTriangleIcon" :size="18" />
          <span>Journal d'alertes</span>
        </NuxtLink>
        <NuxtLink v-if="user && user.role === 'admin'" to="/parametres" class="nav-item">
          <component :is="SettingsIcon" :size="18" />
          <span>Configuration</span>
        </NuxtLink>
      </nav>

      <div class="sidebar-footer" style="padding: 15px 20px; border-top: 1px solid var(--border-color); display: flex; flex-direction: column; gap: 10px;">
        <div v-if="user" style="display: flex; flex-direction: column; gap: 4px;">
          <div style="font-weight: 700; color: var(--text-primary); font-size: 0.85rem; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;">{{ user.nom }}</div>
          <div class="font-mono text-muted" style="font-size: 0.65rem; text-transform: uppercase;">Rôle: {{ user.role }} <span v-if="user.nom_pays">({{ user.nom_pays }})</span></div>
        </div>

        <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
          <div style="display: flex; align-items: center; gap: 8px; font-size: 0.75rem;">
            <span class="led-indicator success" style="width: 6px; height: 6px;"></span>
            <span style="color: var(--text-secondary); font-weight: 500;">Passerelle: Active</span>
          </div>

          <button @click="logout" class="btn btn-secondary font-mono" style="padding: 4px 8px; font-size: 0.65rem; display: flex; align-items: center; gap: 4px;">
            <component :is="LogOutIcon" :size="12" />
            <span>Sortie</span>
          </button>
        </div>
      </div>
    </aside>

    <main class="main-content">
      <header class="header">
        <div class="header-title" style="font-weight: 600; color: var(--text-primary); text-transform: uppercase; font-size: 0.9rem; letter-spacing: 0.5px;">
          {{ pageTitle }}
        </div>

        <div class="header-controls">
          <div style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 0.75rem; text-transform: uppercase; color: var(--text-muted); font-weight: 600;">Filtrer par pays:</span>

            <div v-if="user && user.role === 'employe' && user.nom_pays" class="country-pill-selector" style="opacity: 0.8; pointer-events: none;">
              <button class="country-pill active">
                {{ user.nom_pays }}
              </button>
            </div>

            <div v-else class="country-pill-selector">
              <button
                class="country-pill"
                :class="{ active: selectedCountry === 'Tous' }"
                @click="selectCountry('Tous')"
              >
                Tous
              </button>
              <button
                v-for="c in countries"
                :key="c"
                class="country-pill"
                :class="{ active: selectedCountry === c }"
                @click="selectCountry(c)"
              >
                {{ c }}
              </button>
            </div>
          </div>
        </div>
      </header>

      <div class="page-body">
        <slot />
      </div>
    </main>
  </div>
</template>

<script setup>
import {
  LayoutDashboard as LayoutDashboardIcon,
  Container as ContainerIcon,
  AlertTriangle as AlertTriangleIcon,
  Settings as SettingsIcon,
  Factory as FactoryIcon,
  Activity as ActivityIcon,
  HelpCircle as HelpIcon,
  Cpu as CpuIcon,
  LogOut as LogOutIcon
} from 'lucide-vue-next'

const { selectedCountry, selectCountry, countries } = useCountryState()
const { user, logout } = useAuth()
const route = useRoute()

const pageTitle = computed(() => {
  if (route.path === '/') return 'TABLEAU DE BORD'
  if (route.path.startsWith('/lots')) return 'STOCKS ET TRAÇABILITÉ LOTS'
  if (route.path === '/parc') return 'GESTION DES ENTREPÔTS'
  if (route.path === '/modules') return 'SUPERVISION MODULES IOT'
  if (route.path === '/alertes') return 'LOGS D\'ALERTES QUALITÉ'
  if (route.path === '/changement') return 'PRÉPARATION AU CHANGEMENT AUTOMATISATION'
  if (route.path === '/parametres') return 'PARAMÈTRES SYSTÈME ET SEUILS'
  if (route.path === '/aide') return 'DOCUMENTATION UTILISATEUR'
  return 'CONSOLE PRINCIPALE'
})
</script>
