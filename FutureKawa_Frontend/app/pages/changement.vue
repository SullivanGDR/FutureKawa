<template>
  <div>
    <div style="display: flex; gap: 20px; margin-bottom: 25px; border-bottom: 1px solid var(--color-border);">
      <button
        @click="activeSubSection = 'schema'"
        class="btn"
        :class="activeSubSection === 'schema' ? 'btn-primary' : 'btn-secondary'"
        style="border-bottom-left-radius: 0; border-bottom-right-radius: 0; padding: 10px 20px; border-bottom: none;"
      >
        Schéma d'Automatisation (Livrable 9)
      </button>
      <button
        @click="activeSubSection = 'questionnaire'"
        class="btn"
        :class="activeSubSection === 'questionnaire' ? 'btn-primary' : 'btn-secondary'"
        style="border-bottom-left-radius: 0; border-bottom-right-radius: 0; padding: 10px 20px; border-bottom: none;"
      >
        Questionnaire Cadrage Phase 2 (Livrable 10)
      </button>
    </div>

    <div v-if="activeSubSection === 'schema'">
      <div style="background: rgba(2,132,199,0.05); border: 1px solid var(--color-border); padding: 20px; border-radius: var(--border-radius); margin-bottom: 25px;">
        <h3 style="color: var(--primary-light); text-transform: uppercase; margin-bottom: 8px;">Principe de Régulation Climatique Auto</h3>
        <p style="font-size: 0.9rem; line-height: 1.5; color: var(--text-secondary);">
          Cette modélisation illustre la boucle de contrôle fermée (Closed-Loop Regulation) qui sera déployée en Phase 2 dans les entrepôts. Les capteurs DHT22 envoient les relevés. L'unité centrale calcule l'écart par rapport aux seuils du pays et pilote les actionneurs industriels (chauffage, humidificateur, extracteurs d'air) avec des sécurités de coupure automatique (arrêt d'urgence et mode manuel forcé).
        </p>
      </div>

      <div style="display: grid; grid-template-columns: 1fr 2fr; gap: 25px; margin-bottom: 30px;">
        <div class="table-container" style="margin-bottom: 0; padding: 20px; display: flex; flex-direction: column; gap: 15px;">
          <h4 style="font-size: 0.9rem; text-transform: uppercase; color: var(--primary-light); margin-bottom: 10px;">Simulateur de Conditions</h4>

          <div class="input-group">
            <label class="input-label">Température Remontée: {{ simTemp }}°C</label>
            <input type="range" min="15" max="40" step="0.5" v-model="simTemp" style="accent-color: var(--primary);" />
          </div>

          <div class="input-group">
            <label class="input-label">Humidité Remontée: {{ simHum }}%</label>
            <input type="range" min="30" max="95" step="1" v-model="simHum" style="accent-color: var(--primary);" />
          </div>

          <div style="border-top: 1px solid var(--color-border); padding-top: 15px; display: flex; flex-direction: column; gap: 10px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-size: 0.85rem;">Mode Chauffage:</span>
              <span class="badge" :class="heaterActive ? 'badge-danger' : 'badge-secondary'">
                {{ heaterActive ? 'ACTIVER (ON)' : 'ARRÊT (OFF)' }}
              </span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-size: 0.85rem;">Mode Aération (Ventilos):</span>
              <span class="badge" :class="fanActive ? 'badge-warning' : 'badge-secondary'">
                {{ fanActive ? 'ACTIVER (ON)' : 'ARRÊT (OFF)' }}
              </span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-size: 0.85rem;">Mode Humidificateur:</span>
              <span class="badge" :class="humidifierActive ? 'badge-success' : 'badge-secondary'">
                {{ humidifierActive ? 'ACTIVER (ON)' : 'ARRÊT (OFF)' }}
              </span>
            </div>
          </div>
        </div>

        <div style="background: var(--bg-panel); border: 1px solid var(--color-border); border-radius: var(--border-radius); padding: 20px; display: flex; align-items: center; justify-content: center; min-height: 300px;">
          <svg viewBox="0 0 600 300" style="width: 100%; height: auto;">
            <rect x="20" y="110" width="100" height="80" fill="#0d1322" stroke="var(--color-border)" stroke-width="2" rx="4" />
            <text x="70" y="140" fill="var(--text-primary)" font-size="12" font-weight="bold" text-anchor="middle">Capteurs DHT22</text>
            <text x="70" y="165" fill="#38bdf8" font-size="10" text-anchor="middle" font-family="monospace">{{ simTemp }}°C / {{ simHum }}%</text>

            <path d="M 120 150 L 220 150" stroke="#38bdf8" stroke-width="2" marker-end="url(#arrow)" />

            <rect x="220" y="90" width="160" height="120" fill="#15243f" stroke="var(--primary)" stroke-width="2" rx="4" />
            <text x="300" y="120" fill="#fff" font-size="13" font-weight="bold" text-anchor="middle">Régulateur Central</text>
            <text x="300" y="145" fill="var(--text-secondary)" font-size="10" text-anchor="middle">Consigne Brésil (29°C / 55%)</text>
            <rect x="240" y="165" width="120" height="30" fill="#0b0f17" rx="3" />
            <text x="300" y="184" fill="var(--success)" font-size="10" font-weight="bold" text-anchor="middle" font-family="monospace">
              {{ systemStatusText }}
            </text>

            <path d="M 380 120 L 480 70" stroke="var(--color-border)" stroke-width="2" />
            <path d="M 380 150 L 480 150" stroke="var(--color-border)" stroke-width="2" />
            <path d="M 380 180 L 480 230" stroke="var(--color-border)" stroke-width="2" />

            <rect x="480" y="40" width="100" height="50" :fill="heaterActive ? 'rgba(239, 68, 68, 0.15)' : '#0d1322'" :stroke="heaterActive ? 'var(--danger)' : 'var(--color-border)'" stroke-width="2" rx="4" />
            <text x="530" y="70" :fill="heaterActive ? 'var(--danger)' : 'var(--text-secondary)'" font-size="11" font-weight="bold" text-anchor="middle">Chauffage</text>

            <rect x="480" y="125" width="100" height="50" :fill="fanActive ? 'rgba(245, 158, 11, 0.15)' : '#0d1322'" :stroke="fanActive ? 'var(--warning)' : 'var(--color-border)'" stroke-width="2" rx="4" />
            <text x="530" y="155" :fill="fanActive ? 'var(--warning)' : 'var(--text-secondary)'" font-size="11" font-weight="bold" text-anchor="middle">Extracteurs</text>

            <rect x="480" y="205" width="100" height="50" :fill="humidifierActive ? 'rgba(16, 185, 129, 0.15)' : '#0d1322'" :stroke="humidifierActive ? 'var(--success)' : 'var(--color-border)'" stroke-width="2" rx="4" />
            <text x="530" y="235" :fill="humidifierActive ? 'var(--success)' : 'var(--text-secondary)'" font-size="11" font-weight="bold" text-anchor="middle">Humidificateur</text>

            <defs>
              <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#38bdf8" />
              </marker>
            </defs>
          </svg>
        </div>
      </div>
    </div>

    <div v-else-if="activeSubSection === 'questionnaire'">
      <div style="background: var(--bg-panel); border: 1px solid var(--color-border); border-radius: var(--border-radius); padding: 25px;">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--color-border); padding-bottom: 15px; margin-bottom: 20px;">
          <h3 style="font-size: 1.15rem; font-weight: 600; text-transform: uppercase; color: var(--primary-light);">
            Questionnaire de Cadrage - Automatisation Phase 2
          </h3>
          <button class="btn btn-secondary" @click="printQuestionnaire">
            Exporter en PDF / Imprimer
          </button>
        </div>

        <div style="display: flex; flex-direction: column; gap: 20px;">
          <div>
            <h4 style="font-size: 0.95rem; font-weight: 600; margin-bottom: 8px;">1. Quels sont les objectifs métiers prioritaires attendus de l'automatisation ?</h4>
            <div style="display: flex; flex-direction: column; gap: 8px; margin-left: 10px;">
              <label style="display: flex; align-items: center; gap: 10px; cursor: pointer;">
                <input type="checkbox" v-model="answers.q1" value="pertes" />
                <span>Réduction drastique des pertes de grains de café vert (but principal)</span>
              </label>
              <label style="display: flex; align-items: center; gap: 10px; cursor: pointer;">
                <input type="checkbox" v-model="answers.q1" value="visibilite" />
                <span>Uniformisation des conditions climatiques sans relevé manuel</span>
              </label>
              <label style="display: flex; align-items: center; gap: 10px; cursor: pointer;">
                <input type="checkbox" v-model="answers.q1" value="prevention" />
                <span>Auditabilité simplifiée vis-à-vis des clients Premium</span>
              </label>
            </div>
          </div>

          <div>
            <h4 style="font-size: 0.95rem; font-weight: 600; margin-bottom: 8px;">2. Quelles sont les contraintes de sécurité et d'arrêt d'urgence requises sur site ?</h4>
            <div style="display: flex; flex-direction: column; gap: 8px; margin-left: 10px;">
              <label style="display: flex; align-items: center; gap: 10px; cursor: pointer;">
                <input type="checkbox" v-model="answers.q2" value="valve" />
                <span>Coupure matérielle (Hardware bypass) en cas de surchauffe</span>
              </label>
              <label style="display: flex; align-items: center; gap: 10px; cursor: pointer;">
                <input type="checkbox" v-model="answers.q2" value="alarme" />
                <span>Envoi d'un signal d'alarme sonore sur site lors d'une panne d'extracteur</span>
              </label>
            </div>
          </div>

          <div>
            <h4 style="font-size: 0.95rem; font-weight: 600; margin-bottom: 8px;">3. Limites d'automatisation acceptables (Seuils d'intervention humaine) :</h4>
            <textarea
              v-model="answers.q3"
              class="industrial-input"
              rows="3"
              placeholder="Décrivez les cas où le système doit impérativement redonner le contrôle manuel à l'opérateur (ex: dérive prolongée de plus de 4 heures)..."
            ></textarea>
          </div>

          <div>
            <h4 style="font-size: 0.95rem; font-weight: 600; margin-bottom: 8px;">4. Modalités de maintenance et d'exploitation du système automatisé :</h4>
            <textarea
              v-model="answers.q4"
              class="industrial-input"
              rows="3"
              placeholder="Spécifiez la fréquence de calibration des capteurs DHT22 et la maintenance des ventilateurs (ex: révision trimestrielle)..."
            ></textarea>
          </div>

          <div>
            <h4 style="font-size: 0.95rem; font-weight: 600; margin-bottom: 8px;">5. Priorités de déploiement par zone géographique :</h4>
            <select v-model="answers.q5" class="industrial-select">
              <option value="bresil">Brésil (Prioritaire en raison des variations d'humidité)</option>
              <option value="colombie">Colombie (Prioritaire pour l'expédition)</option>
              <option value="equateur">Équateur</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>

const simTemp = ref(29)
const simHum = ref(55)

const activeSubSection = ref('schema')

const heaterActive = computed(() => simTemp.value < 26)
const fanActive = computed(() => simTemp.value > 32 || simHum.value > 57)
const humidifierActive = computed(() => simHum.value < 53)

const systemStatusText = computed(() => {
  if (heaterActive.value) return "ACTION: CHAUFFAGE"
  if (fanActive.value && humidifierActive.value) return "ACTION: AERATION + HUMID"
  if (fanActive.value) return "ACTION: EXTRACTEUR"
  if (humidifierActive.value) return "ACTION: HUMIDIFICATION"
  return "STABLE - ATTENTE"
})

const answers = ref({
  q1: ['pertes', 'visibilite'],
  q2: ['valve'],
  q3: 'L\'opérateur doit pouvoir forcer manuellement l\'arrêt des extracteurs à tout moment par commutateur physique sur le boîtier.',
  q4: 'Remplacement préventif des capteurs dht22 tous les 18 mois.',
  q5: 'bresil'
})

const printQuestionnaire = () => {
  if (import.meta.client) {
    window.print()
  }
}
</script>
