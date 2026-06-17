import { ref, computed } from 'vue'

export interface User {
  id_utilisateur: number
  email: string
  nom: string
  role: string
  nom_pays: string | null
}

export const useAuth = () => {
  const user = useState<User | null>('auth-user-state', () => null)
  const isLoggedIn = computed(() => !!user.value)
  const { selectCountry } = useCountryState()

  const login = async (email: string, password: string) => {
    try {
      const data = await $fetch<User>('/api/auth/login', {
        method: 'POST',
        body: { email, password }
      })

      user.value = data

      if (import.meta.client) {
        localStorage.setItem('auth-user', JSON.stringify(data))
      }

      if (data.nom_pays) {
        selectCountry(data.nom_pays)
      } else {
        selectCountry('Tous')
      }

      navigateTo('/')

      return data
    } catch (err: any) {
      const msg = err.data?.message || err.message || 'Échec de la connexion'
      throw new Error(msg)
    }
  }

  const logout = () => {
    user.value = null
    if (import.meta.client) {
      localStorage.removeItem('auth-user')
    }
    navigateTo('/login')
  }

  const checkAuth = () => {
    if (import.meta.client) {
      const saved = localStorage.getItem('auth-user')
      if (saved) {
        try {
          user.value = JSON.parse(saved)

          if (user.value?.nom_pays) {
            selectCountry(user.value.nom_pays)
          }
        } catch (e) {
          localStorage.removeItem('auth-user')
        }
      }
    }
  }

  return {
    user,
    isLoggedIn,
    login,
    logout,
    checkAuth
  }
}
