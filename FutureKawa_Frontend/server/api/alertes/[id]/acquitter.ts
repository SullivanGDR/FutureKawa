export default defineEventHandler(async (event) => {
  const method = getMethod(event)
  const id = getRouterParam(event, 'id')
  const query = getQuery(event)
  const pays = query.pays ? String(query.pays) : 'Brésil'

  if (method === 'POST') {
    return await fetchFromCountry(pays, `/alertes/${id}/acquitter`, {
      method: 'POST'
    })
  }
})
