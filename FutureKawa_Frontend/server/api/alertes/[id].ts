export default defineEventHandler(async (event) => {
  const method = getMethod(event)
  const id = getRouterParam(event, 'id')
  const query = getQuery(event)
  const pays = query.pays ? String(query.pays) : 'Brésil'

  if (method === 'DELETE') {
    return await fetchFromCountry(pays, `/alertes/${id}`, {
      method: 'DELETE'
    })
  }

  if (method === 'POST') {
    try {
      return await fetchFromCountry(pays, `/alertes/${id}/acquitter`, {
        method: 'POST'
      })
    } catch (err: any) {
      const detail = err.data?.detail || err.message || "Impossible d'acquitter l'alerte"
      throw createError({
        statusCode: err.statusCode || 400,
        statusMessage: err.statusMessage || 'Bad Request',
        message: detail,
        data: err.data
      })
    }
  }
})
