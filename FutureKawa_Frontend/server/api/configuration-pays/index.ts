export default defineEventHandler(async (event) => {
  const method = getMethod(event)

  if (method === 'GET') {
    const query = getQuery(event)
    const pays = query.pays ? String(query.pays) : null

    if (pays) {
      return await fetchFromCountry(pays, '/configuration-pays')
    } else {
      return await fetchFromAllCountries('/configuration-pays')
    }
  }

  if (method === 'POST') {
    const body = await readBody(event)
    const pays = body.nom_pays || getCountryFromEvent(event)

    try {
      return await fetchFromCountry(pays, '/configuration-pays', {
        method: 'POST',
        body
      })
    } catch (err) {
      if (pays !== 'Brésil') {
        console.log(`[Gateway Warning] Target node ${pays} is offline. Saving configuration to Brazil node database.`)
        return await fetchFromCountry('Brésil', '/configuration-pays', {
          method: 'POST',
          body
        })
      }
      throw err
    }
  }
})
