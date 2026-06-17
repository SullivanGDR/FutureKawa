export default defineEventHandler(async (event) => {
  const method = getMethod(event)
  const query = getQuery(event)
  const pays = query.pays ? String(query.pays) : null

  if (method === 'GET') {
    if (pays) {
      return await fetchFromCountry(pays, '/modules')
    } else {
      return await fetchFromAllCountries('/modules')
    }
  }

  if (method === 'POST') {
    const body = await readBody(event)
    const targetPays = body.nom_pays || pays || 'Brésil'
    return await fetchFromCountry(targetPays, '/modules', {
      method: 'POST',
      body
    })
  }
})
