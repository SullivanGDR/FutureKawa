<template>
  <div>
    <div class="responsive-grid-2-gap25">
      <div class="table-container">
        <div class="table-header-bar">
          <div class="table-title">ÉDITION CONFIGURATION PAYS</div>
        </div>

        <form @submit.prevent="saveConfig" style="padding: 20px;">
          <div class="input-group">
            <label class="input-label">Pays à configurer</label>
            <select v-model="selectedCountryToEdit" class="industrial-select">
              <option value="Brésil">Brésil</option>
              <option value="Colombie">Colombie</option>
              <option value="Équateur">Équateur</option>
            </select>
          </div>

          <div class="input-group">
            <label class="input-label">E-mail du Responsable Local</label>
            <input type="email" v-model="editingConfig.email_responsable" required class="industrial-input" placeholder="ex: exploitation.bresil@futurekawa.com" />
          </div>

          <div class="responsive-grid-form">
            <div class="input-group">
              <label class="input-label">Température Idéale (°C)</label>
              <input type="number" step="0.1" v-model="editingConfig.temp_ideale" required class="industrial-input font-mono" />
            </div>
            <div class="input-group">
              <label class="input-label">Tolérance Température (±°C)</label>
              <input type="number" step="0.1" v-model="editingConfig.tolerance_temp" required class="industrial-input font-mono" />
            </div>
          </div>

          <div class="responsive-grid-form">
            <div class="input-group">
              <label class="input-label">Humidité Idéale (%)</label>
              <input type="number" step="0.1" v-model="editingConfig.hum_ideale" required class="industrial-input font-mono" />
            </div>
            <div class="input-group">
              <label class="input-label">Tolérance Humidité (±%)</label>
              <input type="number" step="0.1" v-model="editingConfig.tolerance_hum" required class="industrial-input font-mono" />
            </div>
          </div>

          <div style="padding: 12px; margin-bottom: 20px; font-size: 0.8rem; background: var(--bg-app); border: 1px solid var(--border-color); color: var(--text-secondary); border-radius: var(--border-radius); line-height: 1.4;">
            * Ces seuils déterminent les alertes climatiques. Si un capteur remonte une mesure au-delà de la tolérance (ex: pour le Brésil, &gt;32°C ou &lt;26°C), une alerte automatique est levée et notifiée au responsable par e-mail.
          </div>

          <div v-if="successMsg" style="margin-bottom: 20px; padding: 12px; background: var(--success-bg); border: 1px solid var(--success); color: var(--success); border-radius: var(--border-radius); font-size: 0.85rem;">
            [SUCCÈS] : {{ successMsg }}
          </div>
          <div v-if="errorMsg" style="margin-bottom: 20px; padding: 12px; background: var(--danger-bg); border: 1px solid var(--danger); color: var(--danger); border-radius: var(--border-radius); font-size: 0.85rem;">
            [ERREUR] : {{ errorMsg }}
          </div>

          <div style="display: flex; justify-content: flex-end;">
            <button type="submit" class="btn btn-primary">Enregistrer la Configuration</button>
          </div>
        </form>
      </div>

      <div class="table-container">
        <div class="table-header-bar">
          <div class="table-title">CONFIGURATIONS EN VIGUEUR</div>
        </div>

        <div style="padding: 20px; display: flex; flex-direction: column; gap: 20px;">
          <div v-for="config in configs" :key="config.nom_pays"
               style="padding: 16px; background: var(--bg-surface-hover); border: 1px solid var(--border-color); border-radius: var(--border-radius);">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); padding-bottom: 8px; margin-bottom: 12px;">
              <span style="font-weight: 700; color: var(--primary); font-size: 1.1rem;">{{ config.nom_pays.toUpperCase() }}</span>
              <span class="badge" :class="config.online !== false ? 'badge-success' : 'badge-danger'">
                {{ config.online !== false ? 'EN LIGNE' : 'HORS LIGNE' }}
              </span>
            </div>

            <div class="responsive-grid-info-small" style="font-size: 0.85rem; line-height: 1.5;">
              <div>
                <span class="text-secondary">Seuils Climatiques:</span>
                <div class="font-mono" style="font-weight: bold; margin-top: 2px;">
                  Temp: {{ config.temp_ideale }}°C (±{{ config.tolerance_temp }}°C)<br />
                  Hum: {{ config.hum_ideale }}% (±{{ config.tolerance_hum }}%)
                </div>
              </div>
              <div>
                <span class="text-secondary">Destinataire Alertes:</span>
                <div class="font-mono" style="font-weight: bold; margin-top: 2px; word-break: break-all;">
                  {{ config.email_responsable }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>

const selectedCountryToEdit = ref('Brésil')
const successMsg = ref('')
const errorMsg = ref('')

const editingConfig = ref({
  nom_pays: 'Brésil',
  email_responsable: '',
  temp_ideale: 29.0,
  hum_ideale: 55.0,
  tolerance_temp: 3.0,
  tolerance_hum: 2.0
})

const { data: configs, refresh: refreshConfigs } = await useFetch('/api/configuration-pays')

watch(selectedCountryToEdit, (newVal) => {
  if (configs.value) {
    const found = configs.value.find(c => c.nom_pays === newVal)
    if (found) {
      editingConfig.value = { ...found }
    } else {
      editingConfig.value = {
        nom_pays: newVal,
        email_responsable: '',
        temp_ideale: newVal === 'Colombie' ? 26.0 : newVal === 'Équateur' ? 31.0 : 29.0,
        hum_ideale: newVal === 'Colombie' ? 80.0 : newVal === 'Équateur' ? 60.0 : 55.0,
        tolerance_temp: 3.0,
        tolerance_hum: 2.0
      }
    }
  }
}, { immediate: true })

watch(configs, (newVal) => {
  if (newVal) {
    const found = newVal.find(c => c.nom_pays === selectedCountryToEdit.value)
    if (found) {
      editingConfig.value = { ...found }
    }
  }
}, { immediate: true })

const saveConfig = async () => {
  successMsg.value = ''
  errorMsg.value = ''
  try {
    editingConfig.value.nom_pays = selectedCountryToEdit.value
    await $fetch('/api/configuration-pays', {
      method: 'POST',
      body: editingConfig.value
    })

    successMsg.value = `Configuration pour le ${selectedCountryToEdit.value} enregistrée.`
    refreshConfigs()
  } catch (err) {
    errorMsg.value = err.data?.detail || err.message || "Erreur d'enregistrement."
  }
}
</script>
