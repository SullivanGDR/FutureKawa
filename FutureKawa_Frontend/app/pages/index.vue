<template>
  <div>
    <div class="industrial-grid">
      <div class="industrial-card primary">
        <div class="card-title">
          <span>Stocks Totaux (Café Vert)</span>
          <component :is="ContainerIcon" :size="16" style="color: var(--primary);" />
        </div>
        <div class="card-value">{{ filteredLots.length }}</div>
        <div class="card-meta">LOTS ENREGISTRÉS</div>
      </div>

      <div class="industrial-card">
        <div class="card-title">
          <span>Exploitations / Entrepôts</span>
          <component :is="FactoryIcon" :size="16" style="color: var(--text-secondary);" />
        </div>
        <div class="card-value">{{ filteredEntrepots.length }}</div>
        <div class="card-meta">SITES DE STOCKAGE</div>
      </div>

      <div class="industrial-card" :class="activeAlertsCount > 0 ? 'danger' : 'success'">
        <div class="card-title">
          <span>Alertes Actives</span>
          <span class="led-indicator" :class="activeAlertsCount > 0 ? 'danger pulse' : 'success'"></span>
        </div>
        <div class="card-value" :style="{ color: activeAlertsCount > 0 ? 'var(--danger)' : 'var(--success)' }">
          {{ activeAlertsCount }}
        </div>
        <div class="card-meta">QUALITÉ & ANCIENNETÉ</div>
      </div>

      <div class="industrial-card" :class="conformityRate > 90 ? 'success' : 'warning'">
        <div class="card-title">
          <span>Taux de Conformité</span>
          <component :is="ActivityIcon" :size="16" :style="{ color: conformityRate > 90 ? 'var(--success)' : 'var(--warning)' }" />
        </div>
        <div class="card-value">{{ conformityRate }}%</div>
        <div class="card-meta">LOTS SANS ANOMALIE</div>
      </div>
    </div>

    <div class="dashboard-row">
      <div class="table-container">
        <div class="table-header-bar">
          <div class="table-title">Dernières anomalies détectées</div>
          <NuxtLink to="/alertes" class="btn btn-secondary" style="padding: 6px 12px; font-size: 0.75rem;">Voir tout</NuxtLink>
        </div>

        <table class="industrial-table" v-if="recentAlerts.length > 0">
          <thead>
            <tr>
              <th>Date</th>
              <th>Pays</th>
              <th>Type d'Alerte</th>
              <th>ID Lot / Module</th>
              <th>Description</th>
              <th>Diagnostic</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="alert in recentAlerts" :key="alert.id_alerte">
              <td>{{ formatDate(alert.date_alerte) }}</td>
              <td>
                <span class="badge" style="background: var(--bg-app); color: var(--text-primary); border: 1px solid var(--border-color);">
                {{ alert.nom_pays }}
              </span>
              </td>
              <td>
                <span class="badge" :class="alert.type_alerte.toLowerCase().includes('cond') ? 'badge-danger' : 'badge-warning'">
                  {{ alert.type_alerte }}
                </span>
              </td>
              <td style="font-weight: 600;">{{ alert.id_lot || alert.id_module }}</td>
              <td>{{ alert.description }}</td>
              <td>
                <span class="led-indicator danger"></span>
                <span class="text-secondary" style="font-size: 0.8rem;">Hors tolérance</span>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-else style="padding: 40px 20px; text-align: center; color: var(--text-muted); font-size: 0.9rem;">
          [ Conformité excellente - aucune alerte active ]
        </div>
      </div>

      <div class="table-container">
        <div class="table-header-bar">
          <div class="table-title">Statuts du réseau</div>
        </div>

        <div style="padding: 20px; display: flex; flex-direction: column; gap: 20px;">
          <div v-for="country in visibleNetworkCountries" :key="country"
               style="display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; background: var(--bg-surface-hover); border: 1px solid var(--border-color); border-radius: var(--border-radius);">
            <div style="display: flex; align-items: center; gap: 10px;">
              <span class="led-indicator" :class="getNodeStatus(country) ? 'success' : 'danger pulse'"></span>
              <span style="font-weight: 600; font-size: 0.9rem;">API {{ country }}</span>
            </div>
            <span :style="{ color: getNodeStatus(country) ? 'var(--success)' : 'var(--danger)' }" style="font-size: 0.8rem; font-weight: 500;">
              {{ getNodeStatus(country) ? 'Actif (200 OK)' : 'Déconnecté' }}
            </span>
          </div>

          <div style="padding: 15px; border-left: 3px solid var(--primary); background-color: rgba(2, 132, 199, 0.05); font-size: 0.85rem; line-height: 1.5; border-radius: var(--border-radius);">
            <strong style="color: var(--primary-light);">Consignes de rotation (FIFO) :</strong>
            <p style="margin-top: 4px; color: var(--text-secondary);">
              Les lots de café vert doivent être expédiés par ordre d'ancienneté. Les lots les plus anciens figurent en priorité haute dans le système de gestion des stocks.
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
  Container as ContainerIcon,
  Factory as FactoryIcon,
  Activity as ActivityIcon
} from 'lucide-vue-next'

const { selectedCountry } = useCountryState()
const { user } = useAuth()

const { data: lots, refresh: refreshLots } = await useFetch('/api/lots')
const { data: entrepots, refresh: refreshEntrepots } = await useFetch('/api/entrepots')
const { data: alertes, refresh: refreshAlertes } = await useFetch('/api/alertes')
const { data: configs, refresh: refreshConfigs } = await useFetch('/api/configuration-pays')

const visibleNetworkCountries = computed(() => {
  if (user.value && user.value.role === 'employe' && user.value.nom_pays) {
    return [user.value.nom_pays]
  }
  return ['Brésil', 'Colombie', 'Équateur']
})

const filteredLots = computed(() => {
  if (!lots.value) return []
  if (selectedCountry.value === 'Tous') return lots.value
  return lots.value.filter(lot => lot.nom_pays === selectedCountry.value)
})

const filteredEntrepots = computed(() => {
  if (!entrepots.value) return []
  if (selectedCountry.value === 'Tous') return entrepots.value
  return entrepots.value.filter(e => e.nom_pays === selectedCountry.value)
})

const filteredAlertes = computed(() => {
  if (!alertes.value) return []
  if (selectedCountry.value === 'Tous') return alertes.value
  return alertes.value.filter(a => a.nom_pays === selectedCountry.value)
})

const activeAlertsCount = computed(() => filteredAlertes.value.length)

const conformityRate = computed(() => {
  if (filteredLots.value.length === 0) return 100
  const conforming = filteredLots.value.filter(l => l.statut?.toLowerCase() === 'conforme').length
  return Math.round((conforming / filteredLots.value.length) * 100)
})

const recentAlerts = computed(() => {
  return [...filteredAlertes.value]
    .sort((a, b) => new Date(b.date_alerte) - new Date(a.date_alerte))
    .slice(0, 5)
})

const getNodeStatus = (country) => {
  if (!configs.value) return false
  const found = configs.value.find(c => c.node_pays === country)
  return found ? found.online !== false : false
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return d.toLocaleString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

let timer
onMounted(() => {
  timer = setInterval(() => {
    refreshLots()
    refreshEntrepots()
    refreshAlertes()
    refreshConfigs()
  }, 10000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>
