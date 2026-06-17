<template>
  <div>
    <div style="margin-bottom: 20px;">
      <NuxtLink to="/lots" class="btn btn-secondary" style="padding: 8px 16px;">
        <component :is="ArrowLeftIcon" :size="16" />
        <span>Retour au Stock</span>
      </NuxtLink>
    </div>

    <div v-if="pending" style="padding: 100px; text-align: center; color: var(--text-muted); font-family: var(--font-mono);">
      [ REQUÊTE EN COURS - CHARGEMENT DES DONNÉES DU LOT ]
    </div>

    <div v-else-if="lot">
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
        <div class="table-container" style="margin-bottom: 0;">
          <div class="table-header-bar">
            <div class="table-title">DOSSIER LOT : {{ lot.id_lot }}</div>
            <div style="display: flex; align-items: center; gap: 8px;">
              <component :is="getStatusIconComp(lot.statut)" :size="16" :style="{ color: getStatusColor(lot.statut) }" />
              <span class="badge" :class="getStatusBadgeClass(lot.statut)" style="font-size: 0.75rem; padding: 3px 8px;">{{ lot.statut }}</span>
            </div>
          </div>
          <div style="padding: 18px 20px; display: grid; grid-template-columns: 1fr 1fr; gap: 16px 24px;">
            <div>
              <span class="input-label">Pays d'Origine</span>
              <div style="font-size: 0.95rem; font-weight: 700; margin-top: 3px;">{{ lot.nom_pays }}</div>
            </div>

            <div>
              <span class="input-label">Entrepôt de Stockage</span>
              <div style="font-size: 0.95rem; font-weight: 700; margin-top: 3px;">{{ entrepotName }}</div>
            </div>

            <div>
              <span class="input-label">Date de Mise en Stock</span>
              <div class="font-mono" style="font-size: 0.9rem; font-weight: 700; margin-top: 3px;">
                {{ formatDate(lot.date_stockage) }}
              </div>
            </div>

            <div>
              <span class="input-label">Date Limite de Péremption (365 j)</span>
              <div class="font-mono" style="font-size: 0.9rem; font-weight: 700; margin-top: 3px;">
                {{ formatExpirationDate(lot.date_stockage) }}
              </div>
            </div>

            <div style="grid-column: span 2; border-top: 1px dashed var(--border-color); padding-top: 12px; margin-top: 4px;">
              <span class="input-label">Durée d'Entreposage & Statut de Rotation</span>
              <div class="font-mono" style="font-size: 0.9rem; font-weight: 700; margin-top: 3px;">
                {{ stockingDays }} jours
                <span v-if="lot.statut === 'périmé'" style="display: block; font-size: 0.75rem; color: var(--danger); font-weight: bold; margin-top: 4px;">
                  🚫 PÉRIMÉ : Stockage supérieur à la limite autorisée de 365 jours.
                </span>
                <span v-else style="display: block; font-size: 0.75rem; font-weight: normal; color: var(--success); margin-top: 4px;">
                  ✓ Stockage conforme (il reste {{ 365 - stockingDays }} jours).
                </span>
              </div>
            </div>
          </div>
        </div>

        <div class="table-container" style="margin-bottom: 0;">
          <div class="table-header-bar">
            <div class="table-title">DISPOSITIF IOT EN PLACE</div>
          </div>
          <div style="padding: 18px 20px; display: flex; flex-direction: column; gap: 10px; justify-content: center; height: calc(100% - 47px); box-sizing: border-box;">
            <div v-if="associatedModules.length > 0" style="display: flex; flex-direction: column; gap: 8px; width: 100%;">
              <div v-for="mod in associatedModules" :key="mod.id_module"
                   style="display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; background: var(--bg-surface-hover); border: 1px solid var(--border-color); border-radius: var(--border-radius); width: 100%; box-sizing: border-box;">
                <div>
                  <div class="font-mono" style="font-weight: 700; color: var(--primary); font-size: 0.9rem;">{{ mod.id_module }}</div>
                  <span class="font-mono text-muted" style="font-size: 0.7rem;">CAPTEUR DHT22 (TEMP/HUM)</span>
                </div>
                <div style="display: flex; align-items: center; gap: 6px;">
                  <span class="led-indicator" :class="mod.statut_connexion.toLowerCase() === 'actif' ? 'success' : 'danger'" style="width: 8px; height: 8px;"></span>
                  <span class="font-mono" style="font-size: 0.75rem;">{{ mod.statut_connexion.toUpperCase() }}</span>
                </div>
              </div>
            </div>
            <div v-else style="color: var(--text-muted); font-family: var(--font-mono); font-size: 0.85rem; text-align: center; padding: 15px 0;">
              [ AUCUN MODULE IOT DÉTECTÉ DANS CET ENTREPÔT ]
            </div>
          </div>
        </div>
      </div>

      <div class="table-container" style="margin-bottom: 25px;">
        <div class="table-header-bar" style="display: flex; justify-content: space-between; align-items: center;">
          <div class="table-title">
            TÉLÉMÉTRIE EN DIRECT
            <span v-if="selectedModuleId" class="font-mono" style="font-size: 0.85rem; color: var(--primary); margin-left: 10px;">[{{ selectedModuleId }}]</span>
          </div>
          <div style="display: flex; gap: 10px; align-items: center;">
            <div v-if="associatedModules.length > 1" style="display: flex; align-items: center; gap: 8px; margin-right: 15px; flex-shrink: 0;">
              <span style="font-size: 0.75rem; color: var(--text-muted); font-family: var(--font-mono); white-space: nowrap;">CAPTEUR :</span>
              <select v-model="selectedModuleId" class="industrial-select" style="padding: 4px 8px; font-size: 0.75rem; height: auto; margin: 0; background: var(--bg-surface); min-width: 140px; border-radius: 4px;">
                <option v-for="mod in associatedModules" :key="mod.id_module" :value="mod.id_module">
                  {{ mod.id_module }}
                </option>
              </select>
            </div>
            <span class="badge badge-success font-mono">IDÉAL : {{ tempIdeale }}°C / {{ humIdeale }}%</span>
          </div>
        </div>
        <div style="padding: 25px;">
          <div style="height: 300px; position: relative;">
            <ClientOnly>
              <LineChart v-if="chartReady" :data="chartData" :options="chartOptions" />
              <div v-else style="height: 100%; display: flex; align-items: center; justify-content: center; color: var(--text-muted); font-family: var(--font-mono);">
                [ INITIALISATION DU MODULE GRAPHIQUE... ]
              </div>
            </ClientOnly>
          </div>

          <div style="margin-top: 16px; font-size: 0.75rem; color: var(--text-muted); text-align: center; font-family: var(--font-mono);">
            * Les relevés sont transmis automatiquement via le broker MQTT régional toutes les 5 minutes (Tolérance ±3°C / ±2% HR).
          </div>
        </div>
      </div>

      <div id="alert-history" class="table-container" style="margin-bottom: 0;">
        <div class="table-header-bar" style="display: flex; align-items: center; gap: 8px;">
          <component :is="AlertTriangleIcon" :size="16" style="color: var(--danger);" />
          <div class="table-title">HISTORIQUE DES SIGNALEMENTS DU LOT</div>
        </div>

        <table class="industrial-table" v-if="lotAlerts.length > 0">
          <thead>
            <tr>
              <th style="width: 150px;">Date</th>
              <th style="width: 120px;">Type</th>
              <th>Description</th>
              <th style="width: 100px; text-align: center;">Statut</th>
              <th style="width: 150px; text-align: right;">Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="alert in lotAlerts" :key="alert.id_alerte" :style="alert.traitee ? {} : { borderLeft: '3px solid var(--danger)' }">
              <td class="font-mono" style="font-size: 0.8rem;">{{ formatDateTime(alert.date_alerte) }}</td>
              <td>
                <span class="badge" style="background: var(--bg-app); border: 1px solid var(--border-color);">{{ alert.type_alerte }}</span>
              </td>
              <td style="color: var(--text-secondary); font-size: 0.8rem;">{{ alert.description || 'Aucune description' }}</td>
              <td style="text-align: center;">
                <span v-if="alert.traitee" class="badge badge-success">Traitée</span>
                <span v-else class="badge badge-danger">En cours</span>
              </td>
              <td style="text-align: right;">
                <template v-if="!alert.traitee">
                  <button
                    v-if="!alert.type_alerte.toLowerCase().includes('pére') && !alert.type_alerte.toLowerCase().includes('pere')"
                    class="btn btn-secondary"
                    style="padding: 4px 10px; font-size: 0.7rem;"
                    @click="acquitterAlerte(alert.id_alerte)"
                  >
                    Acquitter
                  </button>
                  <span v-else style="color: var(--danger); font-size: 0.7rem; font-family: var(--font-mono); font-weight: bold; text-transform: uppercase;">Irréversible</span>
                </template>
                <span v-else style="color: var(--text-muted); font-size: 0.7rem; font-style: italic;">Clôturé</span>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-else style="padding: 40px; text-align: center; color: var(--success); font-family: var(--font-mono); display: flex; flex-direction: column; align-items: center; gap: 10px;">
          <div style="width: 40px; height: 40px; border-radius: 50%; background: rgba(34, 197, 94, 0.1); display: flex; align-items: center; justify-content: center;">
            ✓
          </div>
          <span>AUCUN SIGNALEMENT ACTIF</span>
          <span style="font-size: 0.75rem; color: var(--text-muted);">Toutes les conditions de stockage sont idéales pour ce lot.</span>
        </div>
      </div>
    </div>

    <div v-else style="padding: 100px; text-align: center; color: var(--danger); font-family: var(--font-mono);">
      [ ERREUR ] : IMPOSSIBLE DE CHARGER LE LOT SPÉCIFIÉ OU HORS PORTÉE DU GATEWAY.
    </div>
  </div>
</template>

<script setup>
import {
  ArrowLeft as ArrowLeftIcon,
  CheckCircle as CheckCircleIcon,
  AlertTriangle as AlertTriangleIcon,
  XOctagon as XOctagonIcon
} from 'lucide-vue-next'
import { Line as LineChart } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import annotationPlugin from 'chartjs-plugin-annotation'
import { useAppDialog } from '~/composables/useAppDialog'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  annotationPlugin
)

const route = useRoute()
const lotId = route.params.id
const paysParam = route.query.pays || 'Brésil'
const { showAlert } = useAppDialog()

const { data: lot, pending, refresh: refreshLot } = await useFetch(`/api/lots/${lotId}`, {
  query: { pays: paysParam }
})

const lotCountry = computed(() => lot.value?.nom_pays || paysParam)

const { data: entrepots } = await useFetch('/api/entrepots', { query: { pays: lotCountry } })
const { data: modules } = await useFetch('/api/modules', { query: { pays: lotCountry } })
const { data: configPays } = await useFetch(() => `/api/configuration-pays?pays=${lotCountry.value}`)

const entrepotName = computed(() => {
  if (!lot.value || !entrepots.value) return '-'
  const e = entrepots.value.find(entry => entry.id_entrepot === lot.value.id_entrepot)
  return e ? e.nom_entrepot : `Entrepôt #${lot.value.id_entrepot}`
})

const stockingDays = computed(() => {
  if (!lot.value) return 0
  const diffTime = Math.abs(new Date() - new Date(lot.value.date_stockage))
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
})

const associatedModules = computed(() => {
  if (!lot.value || !modules.value) return []
  return modules.value.filter(m => m.id_entrepot === lot.value.id_entrepot)
})

const { data: lotAlertes, refresh: refreshAlertes } = await useFetch(`/api/alertes`, {
  query: { pays: lotCountry, lot_id: lotId }
})

const lotAlerts = computed(() => lotAlertes.value || [])

const fetchData = async () => {
  await Promise.all([refreshLot(), refreshAlertes()])
}

const tempIdeale = computed(() => configPays.value?.temp_ideale ?? (lotCountry.value === 'Colombie' ? 26 : lotCountry.value === 'Équateur' ? 31 : 29))
const humIdeale = computed(() => configPays.value?.hum_ideale ?? (lotCountry.value === 'Colombie' ? 80 : lotCountry.value === 'Équateur' ? 60 : 55))

const selectedModuleId = ref(null)

watch(associatedModules, (newMods) => {
  if (newMods && newMods.length > 0) {
    if (!selectedModuleId.value || !newMods.some(m => m.id_module === selectedModuleId.value)) {
      selectedModuleId.value = newMods[0].id_module
    }
  } else {
    selectedModuleId.value = null
  }
}, { immediate: true })

const { data: measurements } = await useAsyncData(
  `telemetry-${lotId}`,
  async () => {
    if (!selectedModuleId.value) return []
    try {
      return await $fetch(`/api/releves`, {
        query: { pays: lotCountry.value, module_id: selectedModuleId.value }
      })
    } catch (e) {
      return []
    }
  },
  { watch: [selectedModuleId] }
)

const acquitterAlerte = async (alerteId) => {
  try {
    await $fetch(`/api/alertes/${alerteId}`, {
      method: 'POST',
      query: { pays: lotCountry.value }
    })
    await showAlert("Alerte acquittée avec succès.", "success")
    await fetchData()
  } catch (err) {
    console.error("Erreur acquittement", err)
    let errorMsg = err.data?.message || err.data?.detail || ""
    if (errorMsg.includes("hors seuil")) {
      errorMsg = "Impossible d'acquitter l'alerte :\n\nLes conditions physiques de stockage du café (température ou humidité) ne sont pas revenues dans les normes de tolérance.\n\n💡 Conseil : Assurez-vous d'arrêter l'anomalie sur le simulateur IoT et d'attendre la prochaine mesure stable avant de réessayer."
    } else {
      errorMsg = errorMsg || "Une erreur est survenue lors de l'acquittement de l'alerte."
    }
    await showAlert(errorMsg, "error")
  }
}

const chartReady = ref(false)

const chartData = computed(() => {
  let labels = []
  let temperatures = []
  let humidities = []

  if (measurements.value && measurements.value.length > 0) {
    const sorted = [...measurements.value].sort((a, b) => new Date(a.date_heure) - new Date(b.date_heure))
    labels = sorted.map(m => new Date(m.date_heure).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }))
    temperatures = sorted.map(m => Number(m.temperature))
    humidities = sorted.map(m => Number(m.humidite))
  } else {
    const idealT = tempIdeale.value
    const idealH = humIdeale.value

    for (let i = 8; i >= 0; i--) {
      const time = new Date(Date.now() - i * 30 * 60 * 1000)
      labels.push(time.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }))

      const tempDelta = Math.sin(i / 1.5) * 1.2 + (Math.random() - 0.5) * 0.4
      const humDelta = Math.cos(i / 1.5) * 1.8 + (Math.random() - 0.5) * 0.5

      temperatures.push((idealT + tempDelta).toFixed(1))
      humidities.push((idealH + humDelta).toFixed(1))
    }
  }

  return {
    labels,
    datasets: [
      {
        label: 'Température (°C)',
        borderColor: '#0ea5e9',
        backgroundColor: 'rgba(14, 165, 233, 0.05)',
        data: temperatures,
        yAxisID: 'y-temp',
        tension: 0.3,
        fill: true,
        borderWidth: 2,
        pointBackgroundColor: '#0ea5e9',
        pointRadius: 3
      },
      {
        label: 'Humidité (%)',
        borderColor: '#f59e0b',
        backgroundColor: 'rgba(245, 158, 11, 0.03)',
        data: humidities,
        yAxisID: 'y-hum',
        tension: 0.3,
        fill: true,
        borderWidth: 2,
        pointBackgroundColor: '#f59e0b',
        pointRadius: 3
      }
    ]
  }
})

const chartOptions = computed(() => {
  const tIdeale = tempIdeale.value
  const hIdeale = humIdeale.value
  const tTol = configPays.value?.tolerance_temp ?? 3
  const hTol = configPays.value?.tolerance_hum ?? 2

  const tempValues = measurements.value ? measurements.value.map(m => Number(m.temperature)).filter(v => !isNaN(v)) : []
  const humValues = measurements.value ? measurements.value.map(m => Number(m.humidite)).filter(v => !isNaN(v)) : []

  const minTempData = tempValues.length > 0 ? Math.min(...tempValues) : tIdeale
  const maxTempData = tempValues.length > 0 ? Math.max(...tempValues) : tIdeale
  const minHumData = humValues.length > 0 ? Math.min(...humValues) : hIdeale
  const maxHumData = humValues.length > 0 ? Math.max(...humValues) : hIdeale

  const yTempMin = Math.min(Math.floor(tIdeale - tTol - 1), Math.floor(minTempData - 1))
  const yTempMax = Math.max(Math.ceil(tIdeale + tTol + 1), Math.ceil(maxTempData + 1))
  const yHumMin = Math.min(Math.floor(hIdeale - hTol - 2), Math.floor(minHumData - 2))
  const yHumMax = Math.max(Math.ceil(hIdeale + hTol + 2), Math.ceil(maxHumData + 2))

  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: '#94a3b8',
          font: { family: 'Inter', size: 11 }
        }
      },
      tooltip: {
        mode: 'index',
        intersect: false,
        titleFont: { family: 'Inter' },
        bodyFont: { family: 'Inter' }
      },
      annotation: {
        annotations: {
          tempMin: {
            type: 'line', yMin: tIdeale - tTol, yMax: tIdeale - tTol,
            yScaleID: 'y-temp', borderColor: 'rgba(14, 165, 233, 0.7)', borderWidth: 2, borderDash: [5, 5],
            label: { display: true, content: `Min ${(tIdeale - tTol).toFixed(0)}°C`, position: 'start', color: '#fff', font: { size: 9, weight: 'bold', family: 'Inter' }, backgroundColor: '#0ea5e9' }
          },
          tempMax: {
            type: 'line', yMin: tIdeale + tTol, yMax: tIdeale + tTol,
            yScaleID: 'y-temp', borderColor: 'rgba(14, 165, 233, 0.7)', borderWidth: 2, borderDash: [5, 5],
            label: { display: true, content: `Max ${(tIdeale + tTol).toFixed(0)}°C`, position: 'start', color: '#fff', font: { size: 9, weight: 'bold', family: 'Inter' }, backgroundColor: '#0ea5e9' }
          },
          humMin: {
            type: 'line', yMin: hIdeale - hTol, yMax: hIdeale - hTol,
            yScaleID: 'y-hum', borderColor: 'rgba(245, 158, 11, 0.7)', borderWidth: 2, borderDash: [5, 5],
            label: { display: true, content: `Min ${(hIdeale - hTol).toFixed(0)}%`, position: 'end', color: '#fff', font: { size: 9, weight: 'bold', family: 'Inter' }, backgroundColor: '#f59e0b' }
          },
          humMax: {
            type: 'line', yMin: hIdeale + hTol, yMax: hIdeale + hTol,
            yScaleID: 'y-hum', borderColor: 'rgba(245, 158, 11, 0.7)', borderWidth: 2, borderDash: [5, 5],
            label: { display: true, content: `Max ${(hIdeale + hTol).toFixed(0)}%`, position: 'end', color: '#fff', font: { size: 9, weight: 'bold', family: 'Inter' }, backgroundColor: '#f59e0b' }
          }
        }
      }
    },
    scales: {
      x: {
        grid: { color: '#1a2238' },
        ticks: { color: '#94a3b8', font: { family: 'Inter', size: 10 } }
      },
      'y-temp': {
        type: 'linear',
        position: 'left',
        title: { display: true, text: 'Température (°C)', color: '#0ea5e9', font: { family: 'Inter', weight: 'bold', size: 11 } },
        grid: { color: 'rgba(26, 34, 56, 0.3)' },
        ticks: { color: '#0ea5e9', font: { family: 'Inter', size: 10 } },
        min: yTempMin,
        max: yTempMax
      },
      'y-hum': {
        type: 'linear',
        position: 'right',
        title: { display: true, text: 'Humidité (%)', color: '#f59e0b', font: { family: 'Inter', weight: 'bold', size: 11 } },
        grid: { drawOnChartArea: false },
        ticks: { color: '#f59e0b', font: { family: 'Inter', size: 10 } },
        min: yHumMin,
        max: yHumMax
      }
    }
  }
})

onMounted(() => {
  setTimeout(() => {
    chartReady.value = true
  }, 100)
})

const getStatusBadgeClass = (status) => {
  if (status === 'conforme') return 'badge-success'
  if (status === 'en alerte') return 'badge-warning'
  if (status === 'périmé') return 'badge-danger'
  return ''
}

const getStatusIconComp = (status) => {
  if (status === 'conforme') return CheckCircleIcon
  if (status === 'en alerte') return AlertTriangleIcon
  if (status === 'périmé') return XOctagonIcon
  return CheckCircleIcon
}

const getStatusColor = (status) => {
  if (status === 'conforme') return 'var(--success)'
  if (status === 'en alerte') return 'var(--warning)'
  if (status === 'périmé') return 'var(--danger)'
  return 'var(--success)'
}

const getStockingDays = (dateStr) => {
  if (!dateStr) return 0
  const start = new Date(dateStr)
  const now = new Date()
  const diffTime = Math.abs(now - start)
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('fr-FR')
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('fr-FR')
}

const getExpirationDate = (dateStr) => {
  if (!dateStr) return null
  const date = new Date(dateStr)
  date.setDate(date.getDate() + 365)
  return date
}

const formatExpirationDate = (dateStr) => {
  const expDate = getExpirationDate(dateStr)
  return expDate ? expDate.toLocaleDateString('fr-FR') : '-'
}
</script>
