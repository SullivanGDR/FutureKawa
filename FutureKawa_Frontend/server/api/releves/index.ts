export default defineEventHandler(async (event) => {
  const method = getMethod(event)
  const query = getQuery(event)
  const pays = query.pays ? String(query.pays) : null
  const moduleId = query.module_id ? String(query.module_id) : null

  if (method === 'GET') {
    if (pays) {
      if (moduleId) {
        return await fetchFromCountry(pays, `/releves/module/${moduleId}`)
      }
      return await fetchFromCountry(pays, '/releves')
    } else {
      if (moduleId) {
        const countries = ['Brésil', 'Colombie', 'Équateur']
        for (const c of countries) {
          try {
            const data = await fetchFromCountry(c, `/releves/module/${moduleId}`)
            if (data && data.length > 0) return data
          } catch (e) {
          }
        }
        return []
      }
      return await fetchFromAllCountries('/releves')
    }
  }
})
