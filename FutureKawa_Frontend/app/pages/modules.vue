<template>
  <div>
    <div v-if="!selectedModule">
      <div class="industrial-grid">
        <div class="industrial-card primary">
          <div class="card-title">
            <span>Modules Déployés</span>
            <component :is="CpuIcon" :size="16" style="color: var(--primary);" />
          </div>
          <div class="card-value">{{ filteredModules.length }}</div>
          <div class="card-meta">CAPTEURS IOT ENREGISTRÉS</div>
        </div>

        <div class="industrial-card" :class="activeModulesCount === filteredModules.length ? 'success' : 'warning'">
          <div class="card-title">
            <span>Modules Actifs</span>
            <span class="led-indicator" :class="activeModulesCount === filteredModules.length ? 'success' : 'danger pulse'"></span>
          </div>
          <div class="card-value" :style="{ color: activeModulesCount === filteredModules.length ? 'var(--success)' : 'var(--amber)' }">
            {{ activeModulesCount }} / {{ filteredModules.length }}
          </div>
          <div class="card-meta">CONNEXION MQTT</div>
        </div>

        <div class="industrial-card" :class="modulesEnAlerteCount > 0 ? 'danger' : 'success'">
          <div class="card-title">
            <span>Alertes Module</span>
            <component :is="AlertTriangleIcon" :size="16" :style="{ color: modulesEnAlerteCount > 0 ? 'var(--danger)' : 'var(--success)' }" />
          </div>
          <div class="card-value" :style="{ color: modulesEnAlerteCount > 0 ? 'var(--danger)' : 'var(--success)' }">
            {{ modulesEnAlerteCount }}
          </div>
          <div class="card-meta">ALERTES NON TRAITÉES</div>
        </div>

        <div class="industrial-card">
          <div class="card-title">
            <span>Entrepôts Couverts</span>
            <component :is="WarehouseIcon" :size="16" style="color: var(--text-secondary);" />
          </div>
          <div class="card-value">{{ coveredWarehousesCount }}</div>
          <div class="card-meta">SITES AVEC CAPTEUR</div>
        </div>
      </div>

      <div class="table-container" style="margin-bottom: 0;">
        <div class="table-header-bar">
          <div class="table-title">Inventaire des modules IoT</div>
          <button class="btn btn-primary" @click="openRegisterDialog" style="padding: 6px 14px; font-size: 0.75rem;">
            <component :is="PlusIcon" :size="14" />
            Enregistrer un module
          </button>
        </div>

        <table class="industrial-table" v-if="filteredModules.length > 0">
          <thead>
            <tr>
              <th>Identifiant Module</th>
              <th>Statut</th>
              <th>Entrepôt</th>
              <th>Dernière Température</th>
              <th>Dernière Humidité</th>
              <th>Dernier Signal</th>
              <th style="text-align: right;">Détails</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="mod in filteredModules" :key="mod.id_module">
              <td class="font-mono" style="font-weight: 700;">{{ mod.id_module }}</td>
              <td>
                <div style="display: flex; align-items: center; gap: 8px;">
                  <span class="led-indicator" :class="mod.statut_connexion?.toLowerCase() === 'actif' ? 'success' : 'danger pulse'"></span>
                  <span class="badge" :class="mod.statut_connexion?.toLowerCase() === 'actif' ? 'badge-success' : 'badge-danger'">
                    {{ mod.statut_connexion?.toUpperCase() || 'INCONNU' }}
                  </span>
                </div>
              </td>
              <td>{{ getEntrepotName(mod.id_entrepot) }}</td>
              <td>
                <span v-if="getLastMeasurement(mod.id_module)" class="font-mono" :style="{ color: isTempAlert(mod.id_module) ? 'var(--danger)' : 'var(--text-primary)', fontWeight: isTempAlert(mod.id_module) ? 700 : 400 }">
                  {{ getLastMeasurement(mod.id_module)?.temperature }}°C
                  <component v-if="isTempAlert(mod.id_module)" :is="AlertTriangleIcon" :size="12" style="color: var(--danger); vertical-align: middle; margin-left: 4px;" />
                </span>
                <span v-else class="font-mono" style="color: var(--text-muted);">—</span>
              </td>
              <td>
                <span v-if="getLastMeasurement(mod.id_module)" class="font-mono" :style="{ color: isHumAlert(mod.id_module) ? 'var(--danger)' : 'var(--text-primary)', fontWeight: isHumAlert(mod.id_module) ? 700 : 400 }">
                  {{ getLastMeasurement(mod.id_module)?.humidite }}%
                  <component v-if="isHumAlert(mod.id_module)" :is="AlertTriangleIcon" :size="12" style="color: var(--danger); vertical-align: middle; margin-left: 4px;" />
                </span>
                <span v-else class="font-mono" style="color: var(--text-muted);">—</span>
              </td>
              <td class="font-mono" style="font-size: 0.8rem; color: var(--text-secondary);">
                {{ getLastSignalTime(mod.id_module) }}
              </td>
              <td style="text-align: right;">
                <button class="btn btn-secondary" style="padding: 4px 10px; font-size: 0.7rem;" @click="selectModule(mod)">
                  <component :is="EyeIcon" :size="12" />
                  Inspecter
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-else style="padding: 60px 20px; text-align: center; color: var(--text-muted); font-family: var(--font-mono);">
          [ AUCUN MODULE IOT ENREGISTRÉ POUR CE PAYS ]
        </div>
      </div>
    </div>

    <div v-else>
      <div style="margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;">
        <button class="btn btn-secondary" style="padding: 8px 16px;" @click="selectedModule = null">
          <component :is="ArrowLeftIcon" :size="16" />
          <span>Retour à l'inventaire</span>
        </button>

        <button class="btn btn-secondary" style="padding: 8px 16px;" @click="showHistoryModal = true">
          <component :is="HistoryIcon" :size="16" />
          <span>Historique des alertes</span>
        </button>
      </div>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
        <div class="table-container" style="margin-bottom: 0;">
          <div class="table-header-bar">
            <div class="table-title" style="display: flex; align-items: center; gap: 10px;">
              MODULE : {{ selectedModule.id_module }}
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
              <span class="led-indicator" :class="selectedModule.statut_connexion?.toLowerCase() === 'actif' ? 'success' : 'danger pulse'" style="width: 10px; height: 10px;"></span>
              <span class="badge" :class="selectedModule.statut_connexion?.toLowerCase() === 'actif' ? 'badge-success' : 'badge-danger'" style="font-size: 0.75rem; padding: 3px 8px;">
                {{ selectedModule.statut_connexion?.toUpperCase() }}
              </span>
            </div>
          </div>
          <div style="padding: 18px 20px; display: grid; grid-template-columns: 1fr 1fr; gap: 16px 24px;">
            <div>
              <span class="input-label">Identifiant</span>
              <div class="font-mono" style="font-size: 0.95rem; font-weight: 700; margin-top: 3px;">{{ selectedModule.id_module }}</div>
            </div>
            <div>
              <span class="input-label">Entrepôt</span>
              <div style="font-size: 0.95rem; font-weight: 700; margin-top: 3px;">{{ getEntrepotName(selectedModule.id_entrepot) }}</div>
            </div>
            <div>
              <span class="input-label">Pays</span>
              <div style="font-size: 0.95rem; font-weight: 700; margin-top: 3px;">{{ selectedModule.nom_pays || selectedCountry }}</div>
            </div>
            <div>
              <span class="input-label">Capteur</span>
              <div class="font-mono" style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 3px;">DHT22 (T° / Hum)</div>
            </div>
          </div>
        </div>

        <div class="table-container" style="margin-bottom: 0;">
          <div class="table-header-bar">
            <div class="table-title">Dernières Valeurs</div>
          </div>
          <div style="padding: 18px 20px;">
            <div v-if="detailLastMeasurement" style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
              <div class="industrial-card" :class="isDetailTempAlert ? 'danger' : 'success'" style="margin-bottom: 0;">
                <div class="card-title">
                  <span>Température</span>
                  <component :is="ThermometerIcon" :size="16" :style="{ color: isDetailTempAlert ? 'var(--danger)' : 'var(--success)' }" />
                </div>
                <div class="card-value" :style="{ color: isDetailTempAlert ? 'var(--danger)' : 'var(--text-primary)' }">
                  {{ detailLastMeasurement.temperature }}°C
                </div>
                <div class="card-meta" v-if="detailConfig">
                  SEUIL : {{ detailTempMin }}°C – {{ detailTempMax }}°C
                </div>
              </div>
              <div class="industrial-card" :class="isDetailHumAlert ? 'danger' : 'success'" style="margin-bottom: 0;">
                <div class="card-title">
                  <span>Humidité</span>
                  <component :is="DropletsIcon" :size="16" :style="{ color: isDetailHumAlert ? 'var(--danger)' : 'var(--success)' }" />
                </div>
                <div class="card-value" :style="{ color: isDetailHumAlert ? 'var(--danger)' : 'var(--text-primary)' }">
                  {{ detailLastMeasurement.humidite }}%
                </div>
                <div class="card-meta" v-if="detailConfig">
                  SEUIL : {{ detailHumMin }}% – {{ detailHumMax }}%
                </div>
              </div>
            </div>
            <div v-else style="padding: 20px; text-align: center; color: var(--text-muted); font-family: var(--font-mono);">
              [ AUCUNE MESURE REÇUE ]
            </div>
          </div>
        </div>
      </div>

      <div class="table-container" style="margin-bottom: 0;">
        <div class="table-header-bar" style="display: flex; justify-content: space-between; align-items: center;">
          <div class="table-title">Historique Télémétrie</div>
          <div style="display: flex; gap: 10px;" v-if="detailConfig">
            <span class="badge badge-success font-mono">IDÉAL : {{ detailConfig.temp_ideale }}°C / {{ detailConfig.hum_ideale }}%</span>
          </div>
        </div>
        <div style="padding: 25px;">
          <div style="height: 300px; position: relative;">
            <ClientOnly>
              <LineChart v-if="detailChartReady" :data="detailChartData" :options="detailChartOptions" />
              <div v-else style="height: 100%; display: flex; align-items: center; justify-content: center; color: var(--text-muted); font-family: var(--font-mono);">
                [ INITIALISATION DU MODULE GRAPHIQUE... ]
              </div>
            </ClientOnly>
          </div>
          <div style="margin-top: 16px; font-size: 0.75rem; color: var(--text-muted); text-align: center; font-family: var(--font-mono);">
            * Les relevés sont transmis automatiquement via le broker MQTT régional. Les lignes pointillées représentent les seuils de tolérance.
          </div>
        </div>
      </div>

      <div class="table-container" style="margin-top: 25px;">
        <div class="table-header-bar" style="display: flex; justify-content: space-between; align-items: center;">
          <div class="table-title" style="display: flex; align-items: center; gap: 10px;">
            <component :is="AlertTriangleIcon" :size="16" style="color: var(--danger);" />
            Alertes en cours
            <span v-if="activeAlerts.length > 0" class="badge badge-danger" style="font-size: 0.7rem; padding: 2px 8px; border-radius: 10px; min-width: 22px; text-align: center;">{{ activeAlerts.length }}</span>
          </div>
        </div>
        <table class="industrial-table" v-if="activeAlerts.length > 0">
          <thead>
            <tr>
              <th style="width: 160px;">Date</th>
              <th style="width: 160px;">Type</th>
              <th>Description</th>
              <th style="width: 100px; text-align: center;">Statut</th>
              <th style="width: 130px; text-align: right;">Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="alert in activeAlerts" :key="alert.id_alerte" style="border-left: 3px solid var(--danger);">
              <td class="font-mono" style="font-size: 0.8rem;">{{ formatDateTime(alert.date_alerte) }}</td>
              <td>
                <span class="badge" :class="alert.type_alerte?.includes('connexion') ? 'badge-warning' : 'badge-danger'">
                  {{ alert.type_alerte }}
                </span>
              </td>
              <td style="color: var(--text-secondary); font-size: 0.8rem;">{{ alert.description || '—' }}</td>
              <td style="text-align: center;">
                <span class="badge badge-danger" style="animation: pulse-badge 2s ease-in-out infinite;">Active</span>
              </td>
              <td style="text-align: right;">
                <button
                  class="btn btn-secondary"
                  style="padding: 4px 10px; font-size: 0.7rem;"
                  @click="acquitterAlerte(alert)"
                >
                  Acquitter
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-else style="padding: 40px; text-align: center; color: var(--success); font-family: var(--font-mono); display: flex; flex-direction: column; align-items: center; gap: 10px;">
          <div style="width: 40px; height: 40px; border-radius: 50%; background: rgba(34, 197, 94, 0.1); display: flex; align-items: center; justify-content: center;">
            ✓
          </div>
          <span>AUCUNE ALERTE ACTIVE</span>
          <span style="font-size: 0.75rem; color: var(--text-muted);">Toutes les alertes ont été traitées pour ce module.</span>
        </div>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="showRegisterModal" class="dialog-overlay" @click.self="showRegisterModal = false">
        <div class="dialog-box" style="max-width: 500px;">
          <div style="padding: 20px; border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center;">
            <span style="font-weight: 700; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.5px;">Enregistrer un nouveau module</span>
            <button @click="showRegisterModal = false" style="background: none; border: none; cursor: pointer; color: var(--text-muted);">
              <component :is="XIcon" :size="18" />
            </button>
          </div>
          <div style="padding: 25px 20px; display: flex; flex-direction: column; gap: 16px;">
            <div class="input-group" style="margin-bottom: 0;">
              <label class="input-label">Identifiant du module *</label>
              <input v-model="newModule.id_module" type="text" class="industrial-input" placeholder="Ex: br-santos-03" />
            </div>
            <div class="input-group" style="margin-bottom: 0;">
              <label class="input-label">Entrepôt d'affectation *</label>
              <select v-model="newModule.id_entrepot" class="industrial-select">
                <option value="" disabled>Sélectionner un entrepôt</option>
                <option v-for="e in filteredEntrepots" :key="e.id_entrepot" :value="e.id_entrepot">
                  {{ e.nom_entrepot }}
                </option>
              </select>
            </div>
            <div class="input-group" style="margin-bottom: 0;">
              <label class="input-label">Pays cible</label>
              <input :value="registerCountry" type="text" class="industrial-input" disabled style="background: var(--bg-app); color: var(--text-muted);" />
            </div>
          </div>
          <div style="padding: 15px 20px; border-top: 1px solid var(--border-color); display: flex; gap: 15px; justify-content: flex-end;">
            <button class="btn btn-secondary" @click="showRegisterModal = false">Annuler</button>
            <button class="btn btn-primary" @click="registerModule" :disabled="!newModule.id_module || !newModule.id_entrepot">
              <component :is="PlusIcon" :size="14" />
              Enregistrer
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <Teleport to="body">
      <div v-if="showHistoryModal" class="dialog-overlay" @click.self="showHistoryModal = false">
        <div class="dialog-box" style="max-width: 800px; width: 90%;">
          <div style="padding: 20px; border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center;">
            <span style="font-weight: 700; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.5px; display: flex; align-items: center; gap: 8px;">
              <component :is="HistoryIcon" :size="18" />
              Historique des alertes traitées
              <span v-if="treatedAlerts.length > 0" class="badge badge-success" style="font-size: 0.7rem; padding: 2px 8px; border-radius: 10px;">{{ treatedAlerts.length }}</span>
            </span>
            <button @click="showHistoryModal = false" style="background: none; border: none; cursor: pointer; color: var(--text-muted);">
              <component :is="XIcon" :size="18" />
            </button>
          </div>
          <div style="padding: 8px 20px 0; color: var(--text-muted); font-size: 0.8rem; font-family: var(--font-mono);">
            Module : {{ selectedModule?.id_module }}
          </div>
          <div style="max-height: 400px; overflow-y: auto; padding: 10px 0;">
            <table class="industrial-table" v-if="treatedAlerts.length > 0">
              <thead>
                <tr>
                  <th style="width: 160px;">Date</th>
                  <th style="width: 160px;">Type</th>
                  <th>Description</th>
                  <th style="width: 100px; text-align: center;">Statut</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="alert in treatedAlerts" :key="alert.id_alerte" style="border-left: 3px solid var(--success);">
                  <td class="font-mono" style="font-size: 0.8rem;">{{ formatDateTime(alert.date_alerte) }}</td>
                  <td>
                    <span class="badge" :class="alert.type_alerte?.includes('connexion') ? 'badge-warning' : 'badge-danger'">
                      {{ alert.type_alerte }}
                    </span>
                  </td>
                  <td style="color: var(--text-secondary); font-size: 0.8rem;">{{ alert.description || '—' }}</td>
                  <td style="text-align: center;">
                    <span class="badge badge-success">Traitée</span>
                  </td>
                </tr>
              </tbody>
            </table>
            <div v-else style="padding: 40px; text-align: center; color: var(--text-muted); font-family: var(--font-mono);">
              [ AUCUNE ALERTE TRAITÉE POUR CE MODULE ]
            </div>
          </div>
          <div style="padding: 15px 20px; border-top: 1px solid var(--border-color); display: flex; justify-content: flex-end;">
            <button class="btn btn-secondary" @click="showHistoryModal = false">Fermer</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import {
  Cpu as CpuIcon,
  AlertTriangle as AlertTriangleIcon,
  Warehouse as WarehouseIcon,
  Plus as PlusIcon,
  Eye as EyeIcon,
  ArrowLeft as ArrowLeftIcon,
  Thermometer as ThermometerIcon,
  Droplets as DropletsIcon,
  X as XIcon,
  History as HistoryIcon
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

const { selectedCountry } = useCountryState()
const { showAlert, showConfirm } = useAppDialog()

const { data: modules, refresh: refreshModules } = await useFetch('/api/modules')
const { data: entrepots } = await useFetch('/api/entrepots')
const { data: releves, refresh: refreshReleves } = await useFetch('/api/releves')
const { data: alertes, refresh: refreshAlertes } = await useFetch('/api/alertes')
const { data: configs } = await useFetch('/api/configuration-pays')

const filteredModules = computed(() => {
  if (!modules.value) return []
  if (selectedCountry.value === 'Tous') return modules.value
  return modules.value.filter(m => m.nom_pays === selectedCountry.value)
})

const filteredEntrepots = computed(() => {
  if (!entrepots.value) return []
  if (selectedCountry.value === 'Tous') return entrepots.value
  return entrepots.value.filter(e => e.nom_pays === selectedCountry.value)
})

const activeModulesCount = computed(() =>
  filteredModules.value.filter(m => m.statut_connexion?.toLowerCase() === 'actif').length
)

const modulesEnAlerteCount = computed(() => {
  if (!alertes.value) return 0
  const moduleIds = new Set(filteredModules.value.map(m => m.id_module))
  return alertes.value.filter(a => a.id_module && moduleIds.has(a.id_module) && !a.traitee).length
})

const coveredWarehousesCount = computed(() => {
  const ids = new Set(filteredModules.value.map(m => m.id_entrepot))
  return ids.size
})

const getEntrepotName = (id) => {
  if (!entrepots.value) return `#${id}`
  const e = entrepots.value.find(entry => entry.id_entrepot === id)
  return e ? e.nom_entrepot : `Entrepôt #${id}`
}

const latestMeasurements = computed(() => {
  if (!releves.value) return {}
  const map = {}
  for (const r of releves.value) {
    const existing = map[r.id_module]
    if (!existing || new Date(r.date_heure) > new Date(existing.date_heure)) {
      map[r.id_module] = r
    }
  }
  return map
})

const getLastMeasurement = (moduleId) => latestMeasurements.value[moduleId] || null

const getLastSignalTime = (moduleId) => {
  const m = latestMeasurements.value[moduleId]
  if (!m) return '—'
  return new Date(m.date_heure).toLocaleString('fr-FR', {
    day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit'
  })
}

const getConfigForModule = (moduleId) => {
  if (!configs.value || !modules.value || !entrepots.value) return null
  const mod = modules.value.find(m => m.id_module === moduleId)
  if (!mod) return null
  const pays = mod.nom_pays
  if (!pays) return null
  return configs.value.find(c => c.nom_pays === pays) || null
}

const isTempAlert = (moduleId) => {
  const m = getLastMeasurement(moduleId)
  const config = getConfigForModule(moduleId)
  if (!m || !config) return false
  const temp = Number(m.temperature)
  const min = Number(config.temp_ideale) - Number(config.tolerance_temp)
  const max = Number(config.temp_ideale) + Number(config.tolerance_temp)
  return temp < min || temp > max
}

const isHumAlert = (moduleId) => {
  const m = getLastMeasurement(moduleId)
  const config = getConfigForModule(moduleId)
  if (!m || !config) return false
  const hum = Number(m.humidite)
  const min = Number(config.hum_ideale) - Number(config.tolerance_hum)
  const max = Number(config.hum_ideale) + Number(config.tolerance_hum)
  return hum < min || hum > max
}

const selectedModule = ref(null)
const detailChartReady = ref(false)

const selectModule = (mod) => {
  selectedModule.value = mod
  detailChartReady.value = false
  nextTick(() => {
    setTimeout(() => { detailChartReady.value = true }, 150)
  })
}

const detailReleves = computed(() => {
  if (!selectedModule.value || !releves.value) return []
  return releves.value
    .filter(r => r.id_module === selectedModule.value.id_module)
    .sort((a, b) => new Date(a.date_heure) - new Date(b.date_heure))
})

const detailAlerts = computed(() => {
  if (!selectedModule.value || !alertes.value) return []
  return alertes.value
    .filter(a => a.id_module === selectedModule.value.id_module)
    .sort((a, b) => new Date(b.date_alerte) - new Date(a.date_alerte))
})

const detailLastMeasurement = computed(() => {
  if (!selectedModule.value) return null
  return getLastMeasurement(selectedModule.value.id_module)
})

const detailConfig = computed(() => {
  if (!selectedModule.value) return null
  return getConfigForModule(selectedModule.value.id_module)
})

const detailTempMin = computed(() => {
  if (!detailConfig.value) return '?'
  return (Number(detailConfig.value.temp_ideale) - Number(detailConfig.value.tolerance_temp)).toFixed(1)
})
const detailTempMax = computed(() => {
  if (!detailConfig.value) return '?'
  return (Number(detailConfig.value.temp_ideale) + Number(detailConfig.value.tolerance_temp)).toFixed(1)
})
const detailHumMin = computed(() => {
  if (!detailConfig.value) return '?'
  return (Number(detailConfig.value.hum_ideale) - Number(detailConfig.value.tolerance_hum)).toFixed(1)
})
const detailHumMax = computed(() => {
  if (!detailConfig.value) return '?'
  return (Number(detailConfig.value.hum_ideale) + Number(detailConfig.value.tolerance_hum)).toFixed(1)
})

const isDetailTempAlert = computed(() => {
  if (!detailLastMeasurement.value || !detailConfig.value) return false
  const t = Number(detailLastMeasurement.value.temperature)
  return t < Number(detailTempMin.value) || t > Number(detailTempMax.value)
})

const isDetailHumAlert = computed(() => {
  if (!detailLastMeasurement.value || !detailConfig.value) return false
  const h = Number(detailLastMeasurement.value.humidite)
  return h < Number(detailHumMin.value) || h > Number(detailHumMax.value)
})

const detailChartData = computed(() => {
  let labels = []
  let temperatures = []
  let humidities = []

  if (detailReleves.value.length > 0) {
    labels = detailReleves.value.map(m =>
      new Date(m.date_heure).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
    )
    temperatures = detailReleves.value.map(m => Number(m.temperature))
    humidities = detailReleves.value.map(m => Number(m.humidite))
  } else {
    const idealT = detailConfig.value ? Number(detailConfig.value.temp_ideale) : 29
    const idealH = detailConfig.value ? Number(detailConfig.value.hum_ideale) : 55
    for (let i = 8; i >= 0; i--) {
      const time = new Date(Date.now() - i * 30 * 60 * 1000)
      labels.push(time.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }))
      const tempDelta = Math.sin(i / 1.5) * 1.2 + (Math.random() - 0.5) * 0.4
      const humDelta = Math.cos(i / 1.5) * 1.8 + (Math.random() - 0.5) * 0.5
      temperatures.push(+(idealT + tempDelta).toFixed(1))
      humidities.push(+(idealH + humDelta).toFixed(1))
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

const detailChartOptions = computed(() => {
  const tIdeale = detailConfig.value ? Number(detailConfig.value.temp_ideale) : 29
  const hIdeale = detailConfig.value ? Number(detailConfig.value.hum_ideale) : 55
  const tTol = detailConfig.value ? Number(detailConfig.value.tolerance_temp) : 3
  const hTol = detailConfig.value ? Number(detailConfig.value.tolerance_hum) : 2

  const tempValues = detailReleves.value.map(m => Number(m.temperature)).filter(v => !isNaN(v))
  const humValues = detailReleves.value.map(m => Number(m.humidite)).filter(v => !isNaN(v))

  const minTempData = tempValues.length > 0 ? Math.min(...tempValues) : tIdeale
  const maxTempData = tempValues.length > 0 ? Math.max(...tempValues) : tIdeale
  const minHumData = humValues.length > 0 ? Math.min(...humValues) : hIdeale
  const maxHumData = humValues.length > 0 ? Math.max(...humValues) : hIdeale

  const yTempMin = Math.min(Math.floor(tIdeale - tTol - 1), Math.floor(minTempData - 1))
  const yTempMax = Math.max(Math.ceil(tIdeale + tTol + 1), Math.ceil(maxTempData + 1))
  const yHumMin = Math.min(Math.floor(hIdeale - hTol - 2), Math.floor(minHumData - 2))
  const yHumMax = Math.max(Math.ceil(hIdeale + hTol + 2), Math.ceil(maxHumData + 2))

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: '#71717a',
          font: { family: 'D-DIN', size: 11 }
        }
      },
      tooltip: {
        mode: 'index',
        intersect: false,
        titleFont: { family: 'D-DIN' },
        bodyFont: { family: 'D-DIN' }
      }
    },
    scales: {
      x: {
        grid: { color: '#e4e4e9' },
        ticks: { color: '#71717a', font: { family: 'D-DIN', size: 10 } }
      },
      'y-temp': {
        type: 'linear',
        position: 'left',
        title: { display: true, text: 'Température (°C)', color: '#0ea5e9', font: { family: 'D-DIN', weight: 'bold', size: 11 } },
        grid: { color: 'rgba(228, 228, 233, 0.5)' },
        ticks: { color: '#0ea5e9', font: { family: 'D-DIN', size: 10 } },
        min: yTempMin,
        max: yTempMax
      },
      'y-hum': {
        type: 'linear',
        position: 'right',
        title: { display: true, text: 'Humidité (%)', color: '#f59e0b', font: { family: 'D-DIN', weight: 'bold', size: 11 } },
        grid: { drawOnChartArea: false },
        ticks: { color: '#f59e0b', font: { family: 'D-DIN', size: 10 } },
        min: yHumMin,
        max: yHumMax
      }
    }
  }

  try {
    if (ChartJS.registry.plugins.get('annotation')) {
      options.plugins.annotation = {
        annotations: {
          tempMin: {
            type: 'line', yMin: tIdeale - tTol, yMax: tIdeale - tTol,
            yScaleID: 'y-temp', borderColor: 'rgba(14, 165, 233, 0.7)', borderWidth: 2, borderDash: [5, 5],
            label: { display: true, content: `Min ${(tIdeale - tTol).toFixed(0)}°C`, position: 'start', color: '#fff', font: { size: 9, weight: 'bold', family: 'D-DIN' }, backgroundColor: '#0ea5e9' }
          },
          tempMax: {
            type: 'line', yMin: tIdeale + tTol, yMax: tIdeale + tTol,
            yScaleID: 'y-temp', borderColor: 'rgba(14, 165, 233, 0.7)', borderWidth: 2, borderDash: [5, 5],
            label: { display: true, content: `Max ${(tIdeale + tTol).toFixed(0)}°C`, position: 'start', color: '#fff', font: { size: 9, weight: 'bold', family: 'D-DIN' }, backgroundColor: '#0ea5e9' }
          },
          humMin: {
            type: 'line', yMin: hIdeale - hTol, yMax: hIdeale - hTol,
            yScaleID: 'y-hum', borderColor: 'rgba(245, 158, 11, 0.7)', borderWidth: 2, borderDash: [5, 5],
            label: { display: true, content: `Min ${(hIdeale - hTol).toFixed(0)}%`, position: 'end', color: '#fff', font: { size: 9, weight: 'bold', family: 'D-DIN' }, backgroundColor: '#f59e0b' }
          },
          humMax: {
            type: 'line', yMin: hIdeale + hTol, yMax: hIdeale + hTol,
            yScaleID: 'y-hum', borderColor: 'rgba(245, 158, 11, 0.7)', borderWidth: 2, borderDash: [5, 5],
            label: { display: true, content: `Max ${(hIdeale + hTol).toFixed(0)}%`, position: 'end', color: '#fff', font: { size: 9, weight: 'bold', family: 'D-DIN' }, backgroundColor: '#f59e0b' }
          }
        }
      }
    }
  } catch (e) {  }

  return options
})

const showHistoryModal = ref(false)
const activeAlerts = computed(() => {
  return detailAlerts.value.filter(a => !a.traitee)
})
const treatedAlerts = computed(() => {
  return detailAlerts.value.filter(a => a.traitee === true)
})

const showRegisterModal = ref(false)
const newModule = reactive({
  id_module: '',
  id_entrepot: '',
  statut_connexion: 'actif'
})

const registerCountry = computed(() => {
  return selectedCountry.value === 'Tous' ? 'Brésil' : selectedCountry.value
})

const openRegisterDialog = () => {
  newModule.id_module = ''
  newModule.id_entrepot = ''
  showRegisterModal.value = true
}

const registerModule = async () => {
  if (!newModule.id_module || !newModule.id_entrepot) return

  try {
    await $fetch('/api/modules', {
      method: 'POST',
      body: {
        id_module: newModule.id_module,
        id_entrepot: Number(newModule.id_entrepot),
        statut_connexion: 'actif',
        nom_pays: registerCountry.value
      }
    })
    showRegisterModal.value = false
    await showAlert(`Module "${newModule.id_module}" enregistré avec succès.`)
    await refreshModules()
  } catch (err) {
    console.error('Erreur enregistrement module:', err)
    await showAlert(err.data?.detail || "Erreur lors de l'enregistrement du module.")
  }
}

const acquitterAlerte = async (alert) => {
  const confirmed = await showConfirm(`Voulez-vous acquitter l'alerte "${alert.type_alerte}" du module ${alert.id_module} ?`)
  if (!confirmed) return

  try {
    const pays = alert.nom_pays || selectedCountry.value
    await $fetch(`/api/alertes/${alert.id_alerte}`, {
      method: 'POST',
      query: { pays }
    })
    await showAlert('Alerte acquittée avec succès.', 'success')
    await Promise.all([refreshAlertes(), refreshModules()])
  } catch (err) {
    console.error('Erreur acquittement:', err)
    let errorMsg = err.data?.message || err.data?.detail || ""
    if (errorMsg.includes("hors seuil")) {
      errorMsg = "Impossible d'acquitter l'alerte :\n\nLes capteurs de cet entrepôt mesurent toujours des valeurs physiques en dehors des seuils tolérés.\n\n💡 Conseil : Assurez-vous de désactiver l'anomalie sur le simulateur IoT et d'attendre la prochaine mesure stable avant de réessayer."
    } else {
      errorMsg = errorMsg || "Impossible d'acquitter cette alerte. Vérifiez que les mesures sont revenues dans les seuils."
    }
    await showAlert(errorMsg, "error")
  }
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleString('fr-FR', {
    day: '2-digit', month: '2-digit', year: '2-digit',
    hour: '2-digit', minute: '2-digit'
  })
}

let timer
onMounted(() => {
  timer = setInterval(() => {
    refreshModules()
    refreshReleves()
    refreshAlertes()
  }, 15000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(24, 24, 27, 0.3);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.dialog-box {
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-hover);
  width: 100%;
  max-width: 500px;
}

@keyframes pulse-badge {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>
