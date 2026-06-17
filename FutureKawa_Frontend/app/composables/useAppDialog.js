export const useGlobalDialog = () => useState('globalDialog', () => ({
  isOpen: false,
  message: '',
  isConfirm: false,
  type: 'info',
  resolve: null
}))

export const useAppDialog = () => {
  const state = useGlobalDialog()

  const showAlert = (message, type = 'info') => {
    state.value.message = message
    state.value.type = type
    state.value.isConfirm = false
    state.value.isOpen = true
    return new Promise((resolve) => {
      state.value.resolve = resolve
    })
  }

  const showConfirm = (message) => {
    state.value.message = message
    state.value.type = 'warning'
    state.value.isConfirm = true
    state.value.isOpen = true
    return new Promise((resolve) => {
      state.value.resolve = resolve
    })
  }

  const closeDialog = (result) => {
    if (state.value.resolve) {
      state.value.resolve(result)
    }
    state.value.isOpen = false
  }

  return { state, showAlert, showConfirm, closeDialog }
}
