export default defineNuxtRouteMiddleware((to, from) => {
  if (import.meta.server) return

  const { user, checkAuth } = useAuth()

  if (!user.value) {
    checkAuth()
  }

  if (!user.value && to.path !== '/login') {
    return navigateTo('/login')
  }

  if (user.value && to.path === '/login') {
    return navigateTo('/')
  }

  if (user.value && to.path === '/parametres' && user.value.role !== 'admin') {
    return navigateTo('/')
  }
})
