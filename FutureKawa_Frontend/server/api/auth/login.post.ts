export default defineEventHandler(async (event) => {
  const body = await readBody(event)

  if (!body || !body.email || !body.password) {
    throw createError({
      statusCode: 400,
      message: 'Adresse e-mail et mot de passe requis.'
    })
  }

  const countries = ['Brésil', 'Colombie', 'Équateur']

  const promises = countries.map(async (country) => {
    try {
      const data = await fetchFromCountry(country, '/auth/login', {
        method: 'POST',
        body: {
          email: body.email,
          password: body.password
        }
      })
      if (!data || !data.id_utilisateur) {
        return { success: false }
      }
      return { success: true, user: data, country }
    } catch (err) {
      return { success: false }
    }
  })

  const results = await Promise.all(promises)
  const successful = results.find(r => r.success)

  if (successful && successful.user) {
    return {
      id_utilisateur: successful.user.id_utilisateur,
      email: successful.user.email,
      nom: successful.user.nom,
      role: successful.user.role,
      nom_pays: successful.user.nom_pays
    }
  }

  throw createError({
    statusCode: 401,
    message: 'Identifiants de connexion incorrects.'
  })
})
