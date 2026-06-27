<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; gap: 15px; flex-wrap: wrap;">
      <div style="display: flex; align-items: center; gap: 15px; flex-wrap: wrap; flex-grow: 1;">
        <input
          v-model="searchQuery"
          placeholder="Rechercher un lot par ID..."
          class="industrial-input font-mono"
          style="width: 260px;"
        />

        <select v-model="filterEntrepot" class="industrial-select" style="width: 220px;">
          <option value="">Tous</option>
          <option v-for="e in filteredEntrepots" :key="e.id_entrepot" :value="e.id_entrepot">
            [{{ e.nom_pays.toUpperCase() }}] {{ e.nom_entrepot }}
          </option>
        </select>

        <select v-model="filterStatut" class="industrial-select" style="width: 180px;">
          <option value="">Tous</option>
          <option value="conforme">CONFORME</option>
          <option value="en alerte">EN ALERTE</option>
          <option value="périmé">PÉRIMÉ</option>
        </select>
      </div>

      <button class="btn btn-primary" @click="showAddModal = true">
        <component :is="PlusIcon" :size="16" />
        <span>Enregistrer un Lot</span>
      </button>
    </div>

    <div style="background: rgba(255, 107, 0, 0.05); border: 1px solid var(--color-border); padding: 12px 20px; border-radius: var(--border-radius); display: flex; align-items: center; gap: 15px; margin-bottom: 20px;">
      <component :is="ArrowDownAZIcon" :size="20" style="color: var(--primary);" />
      <div>
        <span style="font-weight: 700; color: var(--primary);">ORDRE D'EXPÉDITION FIFO :</span>
        <span style="font-size: 0.9rem; color: var(--text-secondary); margin-left: 8px;">
          Les lots ci-dessous sont listés par ordre d'ancienneté (le plus ancien en premier). Expédiez en priorité les lots situés en haut de la liste.
        </span>
      </div>
    </div>

    <div class="table-container">
      <table class="industrial-table">
        <thead>
          <tr>
            <th>Ordre FIFO</th>
            <th>ID Lot</th>
            <th>Pays</th>
            <th>Entrepôt</th>
            <th>Date d'Entrée</th>
            <th>Date Péremption</th>
            <th>Durée de Stockage</th>
            <th>Statut</th>
            <th style="text-align: right;">Actions</th>
          </tr>
        </thead>
        <tbody v-if="paginatedLots.length > 0">
          <tr v-for="(lot, idx) in paginatedLots" :key="lot.id_lot">
            <td class="font-mono text-muted" style="width: 80px; font-weight: bold;">
              #{{ String(((currentPage - 1) * itemsPerPage) + idx + 1).padStart(3, '0') }}
            </td>
            <td class="font-mono" style="font-weight: 700;">
              <NuxtLink :to="`/lots/${lot.id_lot}?pays=${lot.nom_pays}`" style="color: var(--primary); text-decoration: none; border-bottom: 1px dashed var(--primary);">
                {{ lot.id_lot }}
              </NuxtLink>
            </td>
            <td>
              <span class="badge" style="background: var(--bg-app); color: var(--text-primary); border: 1px solid var(--border-color);">
                {{ lot.nom_pays }}
              </span>
            </td>
            <td>{{ getEntrepotName(lot.id_entrepot, lot.nom_pays) }}</td>
            <td class="font-mono">{{ formatDate(lot.date_stockage) }}</td>
            <td class="font-mono">
              {{ formatDate(lot.date_peremption) }}
            </td>
            <td class="font-mono">
              {{ getStockingDays(lot.date_stockage) }} jours
            </td>
            <td>
              <div style="display: flex; align-items: center; gap: 10px;">
                <component :is="getStatusIconComp(lot.statut)" :size="20" :style="{ color: getStatusColor(lot.statut) }" />
                <span class="font-mono" style="font-weight: 700; font-size: 0.75rem;" :style="getStatusColorStyle(lot.statut)">
                  {{ lot.statut.toUpperCase() }}
                </span>
              </div>
            </td>
            <td style="text-align: right;">
              <div style="display: flex; gap: 10px; justify-content: flex-end;">
                <NuxtLink :to="`/lots/${lot.id_lot}?pays=${lot.nom_pays}`" class="btn btn-secondary" style="padding: 6px 12px; font-size: 0.75rem;">
                  <component :is="EyeIcon" :size="14" />
                </NuxtLink>
                <button class="btn btn-danger" style="padding: 6px 12px; font-size: 0.75rem;" @click="deleteLot(lot.id_lot, lot.nom_pays)">
                  <component :is="TrashIcon" :size="14" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
        <tbody v-else>
          <tr>
            <td colspan="8" style="padding: 40px; text-align: center; color: var(--text-muted); font-family: var(--font-mono);">
              [ AUCUN LOT EN STOCK CORRESPONDANT AUX CRITÈRES ]
            </td>
          </tr>
        </tbody>
      </table>

      <UiPagination
        v-model="currentPage"
        :total-items="sortedLots.length"
        :items-per-page="itemsPerPage"
      />
    </div>

    <div v-if="showAddModal" style="position: fixed; inset: 0; background: rgba(0,0,0,0.4); z-index: 1000; display: flex; align-items: center; justify-content: center; padding: 20px;">
      <div style="background: var(--bg-panel); border: 1px solid var(--border-color); width: 100%; max-width: 500px; border-radius: var(--border-radius); overflow: hidden; box-shadow: var(--shadow-premium);">
        <div style="padding: 16px 20px; border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center; background: var(--bg-app);">
          <span style="font-family: var(--font-mono); font-weight: 700; color: var(--primary);">ENREGISTRER NOUVEAU LOT</span>
          <button @click="showAddModal = false" style="background: none; border: none; color: var(--text-muted); cursor: pointer; font-size: 1.2rem;">&times;</button>
        </div>

        <form @submit.prevent="createLot" style="padding: 20px;">
          <div class="input-group">
            <label class="input-label">Identifiant du Lot (Unique)</label>
            <input v-model="newLot.id_lot" required class="industrial-input font-mono" placeholder="ex: LOT-COL-2026-004" />
          </div>

          <div class="input-group">
            <label class="input-label">Pays de provenance</label>
            <select v-model="newLot.nom_pays" required class="industrial-select">
              <option v-for="c in countries" :key="c" :value="c">{{ c }}</option>
            </select>
          </div>

          <div class="input-group">
            <label class="input-label">Entrepôt de Stockage</label>
            <select v-model="newLot.id_entrepot" required class="industrial-select">
              <option value="" disabled>-- SÉLECTIONNEZ L'ENTREPÔT --</option>
              <option v-for="e in addFormAvailableEntrepots" :key="e.id_entrepot" :value="e.id_entrepot">
                {{ e.nom_entrepot }}
              </option>
            </select>
          </div>

          <div class="input-group">
            <label class="input-label">Date d'Entrée en Stock</label>
            <input type="date" v-model="newLot.date_stockage" required class="industrial-input font-mono" />
          </div>

          <div class="input-group">
            <label class="input-label">Date de Péremption</label>
            <input type="date" v-model="newLot.date_peremption" required class="industrial-input font-mono" />
          </div>

          <div class="input-group">
            <label class="input-label">Statut Initial</label>
            <select v-model="newLot.statut" class="industrial-select">
              <option value="conforme">CONFORME</option>
              <option value="en alerte">EN ALERTE</option>
              <option value="périmé">PÉRIMÉ</option>
            </select>
          </div>

          <div v-if="formError" style="margin-bottom: 20px; padding: 12px; background: var(--danger-bg); border: 1px solid var(--danger); color: var(--danger); border-radius: var(--border-radius); font-size: 0.85rem;">
            [ERREUR DE SAISIE] : {{ formError }}
          </div>

          <div style="display: flex; gap: 15px; justify-content: flex-end; margin-top: 10px;">
            <button type="button" class="btn btn-secondary" @click="showAddModal = false">Annuler</button>
            <button type="submit" class="btn btn-primary">Enregistrer</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
  Plus as PlusIcon,
  Trash2 as TrashIcon,
  Eye as EyeIcon,
  ArrowDownAZ as ArrowDownAZIcon,
  CheckCircle as CheckCircleIcon,
  AlertTriangle as AlertTriangleIcon,
  XOctagon as XOctagonIcon
} from 'lucide-vue-next'
import { useAppDialog } from '~/composables/useAppDialog'

const { selectedCountry, countries } = useCountryState()
const { showAlert, showConfirm } = useAppDialog()

const searchQuery = ref('')
const filterEntrepot = ref('')
const filterStatut = ref('')
const showAddModal = ref(false)
const formError = ref('')

const newLot = ref({
  id_lot: '',
  nom_pays: 'Brésil',
  id_entrepot: '',
  date_stockage: new Date().toISOString().substring(0, 10),
  date_peremption: '',
  statut: 'conforme'
})

const { data: lots, refresh: refreshLots } = await useFetch('/api/lots')
const { data: entrepots } = await useFetch('/api/entrepots')

const filteredEntrepots = computed(() => {
  if (!entrepots.value) return []
  if (selectedCountry.value === 'Tous') return entrepots.value
  return entrepots.value.filter(e => e.nom_pays === selectedCountry.value)
})

const addFormAvailableEntrepots = computed(() => {
  if (!entrepots.value) return []
  return entrepots.value.filter(e => e.nom_pays === newLot.value.nom_pays)
})

const updateDefaultExpiration = (stockageStr) => {
  if (!stockageStr) return
  const date = new Date(stockageStr)
  date.setDate(date.getDate() + 365)
  newLot.value.date_peremption = date.toISOString().substring(0, 10)
}

watch(() => newLot.value.date_stockage, (newVal) => {
  updateDefaultExpiration(newVal)
})

watch(() => newLot.value.nom_pays, (newVal) => {
  const matching = entrepots.value?.filter(e => e.nom_pays === newVal) || []
  newLot.value.id_entrepot = matching.length > 0 ? matching[0].id_entrepot : ''
})

onMounted(() => {
  updateDefaultExpiration(newLot.value.date_stockage)
  if (entrepots.value) {
    const matching = entrepots.value.filter(e => e.nom_pays === newLot.value.nom_pays)
    if (matching.length > 0) {
      newLot.value.id_entrepot = matching[0].id_entrepot
    }
  }
})

const sortedLots = computed(() => {
  if (!lots.value) return []

  let result = [...lots.value]

  if (selectedCountry.value !== 'Tous') {
    result = result.filter(lot => lot.nom_pays === selectedCountry.value)
  }

  if (searchQuery.value) {
    const query = searchQuery.value.trim().toLowerCase()
    result = result.filter(lot => lot.id_lot.toLowerCase().includes(query))
  }

  if (filterEntrepot.value) {
    result = result.filter(lot => lot.id_entrepot === Number(filterEntrepot.value))
  }

  if (filterStatut.value) {
    result = result.filter(lot => lot.statut === filterStatut.value)
  }

  return result.sort((a, b) => new Date(a.date_stockage) - new Date(b.date_stockage))
})

const currentPage = ref(1)
const itemsPerPage = ref(15)

const paginatedLots = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  return sortedLots.value.slice(start, start + itemsPerPage.value)
})

watch([selectedCountry, searchQuery, filterEntrepot, filterStatut], () => {
  currentPage.value = 1
})

const getEntrepotName = (id, country) => {
  if (!entrepots.value) return `Entrepôt #${id}`
  const found = entrepots.value.find(e => e.id_entrepot === id && e.nom_pays === country)
  return found ? found.nom_entrepot : `Entrepôt #${id}`
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

const getStockingDays = (dateStr) => {
  if (!dateStr) return 0
  const diffTime = Math.abs(new Date() - new Date(dateStr))
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
}

const getStatusColorStyle = (status) => {
  if (status === 'conforme') return { color: 'var(--success)' }
  if (status === 'en alerte') return { color: 'var(--warning)' }
  if (status === 'périmé') return { color: 'var(--danger)' }
  return {}
}

const getStatusColor = (status) => {
  if (status === 'conforme') return 'var(--success)'
  if (status === 'en alerte') return 'var(--warning)'
  if (status === 'périmé') return 'var(--danger)'
  return 'var(--success)'
}

const getStatusIconComp = (status) => {
  if (status === 'conforme') return CheckCircleIcon
  if (status === 'en alerte') return AlertTriangleIcon
  if (status === 'périmé') return XOctagonIcon
  return CheckCircleIcon
}

const createLot = async () => {
  formError.value = ''
  try {
    const response = await $fetch('/api/lots', {
      method: 'POST',
      body: {
        id_lot: newLot.value.id_lot,
        date_stockage: newLot.value.date_stockage,
        date_peremption: newLot.value.date_peremption,
        statut: newLot.value.statut,
        id_entrepot: Number(newLot.value.id_entrepot),
        nom_pays: newLot.value.nom_pays
      }
    })

    refreshLots()
    showAddModal.value = false

    newLot.value.id_lot = ''
  } catch (err) {
    formError.value = err.data?.detail || err.message || "Impossible d'enregistrer le lot."
  }
}

const updateLotStatus = async (id, country, newStatus) => {
  try {
    await $fetch(`/api/lots/${id}`, {
      method: 'PATCH',
      query: { pays: country, statut: newStatus }
    })
    refreshLots()
  } catch (err) {
    await showAlert(`Erreur de mise à jour: ${err.message}`)
  }
}

const deleteLot = async (id, country) => {
  if (!await showConfirm(`Confirmez-vous la suppression définitive du lot ${id} ?`)) return
  try {
    await $fetch(`/api/lots/${id}`, {
      method: 'DELETE',
      query: { pays: country }
    })
    refreshLots()
  } catch (err) {
    await showAlert(`Erreur de suppression: ${err.message}`)
  }
}

</script>
