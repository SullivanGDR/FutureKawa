export default defineEventHandler(async (event) => {
  const method = getMethod(event)
  const id = getRouterParam(event, 'id')
  const pays = getCountryFromEvent(event)

  if (method === 'DELETE') {
    return await fetchFromCountry(pays, `/entrepots/${id}`, {
      method: 'DELETE'
    })
  }

  if (method === 'GET') {
    return await fetchFromCountry(pays, `/entrepots/${id}`)
  }
})
