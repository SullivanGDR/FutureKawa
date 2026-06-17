export default defineEventHandler(async (event) => {
  const method = getMethod(event)
  const id = getRouterParam(event, 'id')

  const query = getQuery(event)
  let pays = query.pays ? String(query.pays) : null

  if (method === 'GET') {
    if (pays) {
      return await fetchFromCountry(pays, `/lots/${id}`)
    } else {
      const countries = ['Brésil', 'Colombie', 'Équateur']
      const results = await Promise.allSettled(
        countries.map(c => fetchFromCountry(c, `/lots/${id}`))
      )

      for (const res of results) {
        if (res.status === 'fulfilled' && res.value) {
          return res.value
        }
      }

      throw createError({
        statusCode: 404,
        statusMessage: `Lot ${id} non trouvé dans aucun pays`
      })
    }
  }

  if (method === 'PATCH') {
    const body = await readBody(event)
    const statut = body.statut || query.statut
    if (!pays) {
      pays = body.nom_pays || 'Brésil'
    }

    return await fetchFromCountry(pays, `/lots/${id}/statut`, {
      method: 'PATCH',
      query: { statut }
    })
  }

  if (method === 'DELETE') {
    if (!pays) {
      pays = 'Brésil'
    }
    return await fetchFromCountry(pays, `/lots/${id}`, {
      method: 'DELETE'
    })
  }
})
