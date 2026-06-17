export default defineEventHandler(async (event) => {
  const method = getMethod(event)
  const query = getQuery(event)
  const pays = query.pays ? String(query.pays) : null
  const lotId = query.lot_id ? String(query.lot_id) : null
  const entrepotId = query.entrepot_id ? String(query.entrepot_id) : null
  const moduleId = query.module_id ? String(query.module_id) : null

  if (method === 'GET') {
    if (pays) {
      if (lotId) {
        return await fetchFromCountry(pays, `/alertes/lot/${lotId}`)
      }
      if (entrepotId) {
        return await fetchFromCountry(pays, `/alertes/entrepot/${entrepotId}`)
      }
      if (moduleId) {
        return await fetchFromCountry(pays, `/alertes/module/${moduleId}`)
      }
      return await fetchFromCountry(pays, '/alertes')
    } else {
      if (lotId) {
        return await fetchFromAllCountries(`/alertes/lot/${lotId}`)
      }
      if (entrepotId) {
        return await fetchFromAllCountries(`/alertes/entrepot/${entrepotId}`)
      }
      if (moduleId) {
        return await fetchFromAllCountries(`/alertes/module/${moduleId}`)
      }
      return await fetchFromAllCountries('/alertes')
    }
  }

  if (method === 'POST') {
    const body = await readBody(event)
    const targetPays = body.nom_pays || pays || 'Brésil'
    return await fetchFromCountry(targetPays, '/alertes', {
      method: 'POST',
      body
    })
  }
})
