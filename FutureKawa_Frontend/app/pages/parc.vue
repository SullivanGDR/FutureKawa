<template>
  <div>
    <div>
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <h3 style="font-size: 1.1rem; font-weight: 600; text-transform: uppercase;">Liste des Sites de Stockage</h3>
        <button class="btn btn-primary" @click="showAddEntrepotModal = true">
          <component :is="PlusIcon" :size="16" />
          <span>Ajouter un Entrepôt</span>
        </button>
      </div>

      <div class="table-container">
        <table class="industrial-table">
          <thead>
            <tr>
              <th>ID Site</th>
              <th>Nom de l'Entrepôt</th>
              <th>Zone / Pays</th>
              <th>Lots Actuels</th>
              <th>Dispositifs IoT connectés</th>
              <th style="text-align: right;">Action</th>
            </tr>
          </thead>
          <tbody v-if="paginatedEntrepots.length > 0">
            <tr v-for="ent in paginatedEntrepots" :key="ent.id_entrepot">
              <td style="font-weight: 600; color: var(--primary-light);">ENT-{{ String(ent.id_entrepot).padStart(3, '0') }}</td>
              <td style="font-weight: 600;">{{ ent.nom_entrepot }}</td>
              <td>
                <span class="badge" style="background: var(--bg-app); color: var(--text-primary); border: 1px solid var(--border-color);">
                  {{ ent.nom_pays }}
                </span>
              </td>
              <td>{{ getLotsCountForEntrepot(ent.id_entrepot, ent.nom_pays) }} lots</td>
              <td>{{ getModulesCountForEntrepot(ent.id_entrepot, ent.nom_pays) }} modules</td>
              <td style="text-align: right;">
                <button class="btn btn-danger" style="padding: 6px 12px; font-size: 0.75rem;" @click="deleteEntrepot(ent.id_entrepot, ent.nom_pays)">
                  <component :is="TrashIcon" :size="14" />
                </button>
              </td>
            </tr>
          </tbody>
          <tbody v-else>
            <tr>
              <td colspan="6" style="padding: 40px; text-align: center; color: var(--text-muted);">
                [ AUCUN ENTREPÔT TROUVÉ SUR CETTE ZONE ]
              </td>
            </tr>
          </tbody>
        </table>

        <UiPagination
          v-model="currentEntrepotPage"
          :total-items="filteredEntrepots.length"
          :items-per-page="10"
        />
      </div>
    </div>

    <div v-if="showAddEntrepotModal" style="position: fixed; inset: 0; background: rgba(0,0,0,0.4); z-index: 1000; display: flex; align-items: center; justify-content: center; padding: 20px;">
      <div style="background: var(--bg-panel); border: 1px solid var(--border-color); width: 100%; max-width: 500px; border-radius: var(--border-radius); overflow: hidden; box-shadow: var(--shadow-premium);">
        <div style="padding: 16px 20px; border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center; background: var(--bg-app);">
          <span style="font-weight: 600; color: var(--text-primary);">AJOUTER UN ENTREPÔT</span>
          <button @click="showAddEntrepotModal = false" style="background: none; border: none; color: var(--text-muted); cursor: pointer; font-size: 1.2rem;">&times;</button>
        </div>

        <form @submit.prevent="createEntrepot" style="padding: 20px;">
          <div class="input-group">
            <label class="input-label">Nom de l'Entrepôt</label>
            <input v-model="newEntrepot.nom_entrepot" required class="industrial-input" placeholder="ex: Hub Central - São Paulo" />
          </div>

          <div class="input-group">
            <label class="input-label">Pays</label>
            <select v-model="newEntrepot.nom_pays" required class="industrial-select">
              <option v-for="c in countries" :key="c" :value="c">{{ c }}</option>
            </select>
          </div>

          <div style="display: flex; gap: 10px; justify-content: flex-end; margin-top: 15px;">
            <button type="button" class="btn btn-secondary" @click="showAddEntrepotModal = false">Annuler</button>
            <button type="submit" class="btn btn-primary">Enregistrer</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Plus as PlusIcon, Trash2 as TrashIcon } from 'lucide-vue-next'
import { useAppDialog } from '~/composables/useAppDialog'

const { selectedCountry, countries } = useCountryState()
const { showAlert, showConfirm } = useAppDialog()



const showAddEntrepotModal = ref(false)

const newEntrepot = ref({ nom_entrepot: '', nom_pays: 'Brésil' })

const { data: entrepots, refresh: refreshEntrepots } = await useFetch('/api/entrepots')
const { data: modules } = await useFetch('/api/modules')
const { data: lots } = await useFetch('/api/lots')

const filteredEntrepots = computed(() => {
  if (!entrepots.value) return []
  if (selectedCountry.value === 'Tous') return entrepots.value
  return entrepots.value.filter(e => e.nom_pays === selectedCountry.value)
})

const currentEntrepotPage = ref(1)

const paginatedEntrepots = computed(() => {
  const start = (currentEntrepotPage.value - 1) * 10
  return filteredEntrepots.value.slice(start, start + 10)
})

watch(selectedCountry, () => {
  currentEntrepotPage.value = 1
})



const getLotsCountForEntrepot = (id, country) => {
  if (!lots.value) return 0
  return lots.value.filter(l => l.id_entrepot === id && l.nom_pays === country).length
}

const getModulesCountForEntrepot = (id, country) => {
  if (!modules.value) return 0
  return modules.value.filter(m => m.id_entrepot === id && m.nom_pays === country).length
}

const getEntrepotName = (id, country) => {
  if (!entrepots.value) return `Entrepôt #${id}`
  const found = entrepots.value.find(e => e.id_entrepot === id && e.nom_pays === country)
  return found ? found.nom_entrepot : `Entrepôt #${id}`
}

const createEntrepot = async () => {
  try {
    await $fetch('/api/entrepots', {
      method: 'POST',
      body: newEntrepot.value
    })
    refreshEntrepots()
    showAddEntrepotModal.value = false
  } catch (err) {
    await showAlert(`Erreur de création: ${err.message}`)
  }
}

const deleteEntrepot = async (id, country) => {
  if (!await showConfirm("Voulez-vous supprimer cet entrepôt ? Cela peut détacher les lots associés.")) return
  try {
    await $fetch(`/api/entrepots/${id}`, {
      method: 'DELETE',
      query: { pays: country }
    })
    refreshEntrepots()
  } catch (err) {
    await showAlert(`Erreur de suppression: ${err.message}`)
  }
}



</script>
