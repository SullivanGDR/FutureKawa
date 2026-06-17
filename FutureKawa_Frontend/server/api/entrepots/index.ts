export default defineEventHandler(async (event) => {
  const method = getMethod(event)

  if (method === 'GET') {
    const query = getQuery(event)
    const pays = query.pays ? String(query.pays) : null

    if (pays) {
      return await fetchFromCountry(pays, '/entrepots')
    } else {
      return await fetchFromAllCountries('/entrepots')
    }
  }

  if (method === 'POST') {
    const body = await readBody(event)
    const pays = body.nom_pays || getCountryFromEvent(event)

    return await fetchFromCountry(pays, '/entrepots', {
      method: 'POST',
      body
    })
  }
})
