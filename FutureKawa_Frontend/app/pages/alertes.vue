<template>
  <div>
    <div class="industrial-grid" style="grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); margin-bottom: 25px;">
      <div class="industrial-card danger">
        <div class="card-title">
          <span>Hors Seuils Climatiques</span>
          <component :is="ThermometerIcon" :size="16" style="color: var(--danger);" />
        </div>
        <div class="card-value">{{ climateAlertsCount }}</div>
        <div class="card-meta font-mono">DÉVIATIONS DE TEMP/HUMIDITÉ</div>
      </div>

      <div class="industrial-card warning">
        <div class="card-title">
          <span>Retards de Rotation (FIFO)</span>
          <component :is="ClockIcon" :size="16" style="color: var(--warning);" />
        </div>
        <div class="card-value">{{ agingAlertsCount }}</div>
        <div class="card-meta font-mono">STOCKAGE > 365 JOURS</div>
      </div>
    </div>

    <div class="table-container">
      <div class="table-header-bar">
        <div class="table-title">JOURNAL D'ÉVÉNEMENTS ET INCIDENTS</div>
        <button class="btn btn-secondary" style="padding: 6px 12px; font-size: 0.75rem;" @click="refreshAlertes">
          Actualiser
        </button>
      </div>

      <table class="industrial-table">
        <thead>
          <tr>
            <th>Date & Heure</th>
            <th>Pays</th>
            <th>Type d'Alerte</th>
            <th>Source (Lot/Module)</th>
            <th>Description / Cause</th>
            <th style="width: 120px; text-align: center;">Statut</th>
            <th style="width: 140px; text-align: right;">Action</th>
          </tr>
        </thead>
        <tbody v-if="paginatedAlertes.length > 0">
          <tr v-for="alert in paginatedAlertes" :key="alert.id_alerte">
            <td class="font-mono">{{ formatDate(alert.date_alerte) }}</td>
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
            <td class="font-mono">
              <span v-if="alert.id_lot" style="font-weight: 700;">
                <NuxtLink :to="`/lots/${alert.id_lot}?pays=${alert.nom_pays}`" style="color: var(--primary); text-decoration: none; border-bottom: 1px dashed var(--primary-light);">
                  {{ alert.id_lot }}
                </NuxtLink>
              </span>
              <span v-else class="text-secondary" style="font-weight: 500;">{{ alert.id_module }}</span>
            </td>
            <td>{{ alert.description || 'Valeurs hors seuils' }}</td>
            <td style="text-align: center;">
              <span v-if="alert.traitee" class="badge badge-success">Traitée</span>
              <span v-else class="badge badge-danger">En cours</span>
            </td>
            <td style="text-align: right;">
              <template v-if="!alert.traitee">
                <button
                  v-if="!alert.type_alerte.toLowerCase().includes('pére') && !alert.type_alerte.toLowerCase().includes('pere')"
                  class="btn btn-secondary"
                  style="padding: 6px 12px; font-size: 0.75rem;"
                  @click="acquitterAlerte(alert)"
                >
                  Acquitter
                </button>
                <span v-else style="color: var(--danger); font-size: 0.75rem; font-family: var(--font-mono); font-weight: bold; text-transform: uppercase; padding-right: 10px;">Irréversible</span>
              </template>
              <span v-else style="color: var(--text-muted); font-size: 0.75rem; font-style: italic; font-weight: 600;">Clôturé</span>
            </td>
          </tr>
        </tbody>
        <tbody v-else>
          <tr>
            <td colspan="6" style="padding: 40px; text-align: center; color: var(--text-muted); font-family: var(--font-mono);">
              [ AUCUNE ALERTE ACTIVE SIGNALÉE SUR LE RÉSEAU DE PRODUCTION ]
            </td>
          </tr>
        </tbody>
      </table>

      <UiPagination
        v-model="currentPage"
        :total-items="filteredAlertes.length"
        :items-per-page="itemsPerPage"
      />
    </div>
  </div>
</template>

<script setup>
import {
  Thermometer as ThermometerIcon,
  Clock as ClockIcon
} from 'lucide-vue-next'
import { useAppDialog } from '~/composables/useAppDialog'

const { selectedCountry } = useCountryState()
const { showAlert } = useAppDialog()

const { data: alertes, refresh: refreshAlertes } = await useFetch('/api/alertes')

const filteredAlertes = computed(() => {
  if (!alertes.value) return []
  let list = [...alertes.value]
  if (selectedCountry.value !== 'Tous') {
    list = list.filter(a => a.nom_pays === selectedCountry.value)
  }
  return list.sort((a, b) => new Date(b.date_alerte) - new Date(a.date_alerte))
})

const currentPage = ref(1)
const itemsPerPage = ref(10)

const paginatedAlertes = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  return filteredAlertes.value.slice(start, start + itemsPerPage.value)
})

watch(selectedCountry, () => {
  currentPage.value = 1
})

const climateAlertsCount = computed(() => {
  return filteredAlertes.value.filter(a => a.type_alerte.toLowerCase().includes('cond')).length
})

const processAlertsCount = computed(() => {
  return filteredAlertes.value.filter(a => a.type_alerte.toLowerCase().includes('proc')).length
})

const maintenanceAlertsCount = computed(() => {
  return filteredAlertes.value.filter(a => a.type_alerte.toLowerCase().includes('maint')).length
})

const unresolvedAlertsCount = computed(() => {
  return filteredAlertes.value.filter(a => !a.traitee).length
})

const agingAlertsCount = computed(() => {
  return filteredAlertes.value.filter(a => a.type_alerte.toLowerCase().includes('ancien') || a.type_alerte.toLowerCase().includes('pere') || a.type_alerte.toLowerCase().includes('pére')).length
})

const acquitterAlerte = async (alert) => {
  try {
    const pays = alert.nom_pays || selectedCountry.value
    await $fetch(`/api/alertes/${alert.id_alerte}`, {
      method: 'POST',
      query: { pays }
    })
    await showAlert("Alerte acquittée avec succès.", "success")
    await refreshAlertes()
  } catch (err) {
    console.error("Erreur acquittement", err)
    let errorMsg = err.data?.message || err.data?.detail || ""
    if (errorMsg.includes("hors seuil")) {
      errorMsg = "Impossible d'acquitter l'alerte :\n\nLes capteurs de cet entrepôt relèvent toujours des mesures physiques hors des seuils autorisés.\n\n💡 Conseil : Arrêtez l'anomalie sur le simulateur IoT et attendez que les mesures se stabilisent avant d'acquitter."
    } else {
      errorMsg = errorMsg || "Impossible d'acquitter cette alerte."
    }
    await showAlert(errorMsg, "error")
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('fr-FR')
}

const resolveAlerte = async (id, country) => {
  try {
    await $fetch(`/api/alertes/${id}`, {
      method: 'DELETE',
      query: { pays: country }
    })
    refreshAlertes()
  } catch (err) {
    await showAlert(`Impossible d'acquitter l'alerte : ${err.message}`, "error")
  }
}

</script>
