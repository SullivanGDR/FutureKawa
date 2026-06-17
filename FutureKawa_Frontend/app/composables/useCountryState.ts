export const useCountryState = () => {
  const selectedCountry = useState<string>('selected-country', () => 'Brésil')

  const selectCountry = (country: string) => {
    selectedCountry.value = country
    if (import.meta.client) {
      localStorage.setItem('selected-country', country)
    }
  }

  onMounted(() => {
    if (import.meta.client) {
      const saved = localStorage.getItem('selected-country')
      if (saved) {
        selectedCountry.value = saved
      }
    }
  })

  return {
    selectedCountry,
    selectCountry,
    countries: ['Brésil', 'Colombie', 'Équateur']
  }
}
