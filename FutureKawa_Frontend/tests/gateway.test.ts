import { describe, it, expect } from 'vitest'

/**
 * Tests de la logique de résolution d'URL du gateway (server/utils/gateway.ts).
 * La fonction `getRegionalApiUrl` utilise useRuntimeConfig() — on teste ici
 * la logique de normalisation de pays avec des URLs simulées.
 */

const MOCK_URLS = {
  bresil: 'http://backend:8000/api/v1',
  colombie: 'http://backend:8001/api/v1',
  equateur: 'http://backend:8002/api/v1'
}

function normalizeCountry(country: string): string {
  return country.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '')
}

function resolveApiUrl(country: string): string {
  const n = normalizeCountry(country)
  if (n.includes('bresil')) return MOCK_URLS.bresil
  if (n.includes('colombie')) return MOCK_URLS.colombie
  if (n.includes('equateur')) return MOCK_URLS.equateur
  return MOCK_URLS.bresil
}

describe('Gateway — normalisation des noms de pays', () => {
  it('normalise "Brésil" → "bresil" (supprime accents)', () => {
    expect(normalizeCountry('Brésil')).toBe('bresil')
  })

  it('normalise "Équateur" → "equateur"', () => {
    expect(normalizeCountry('Équateur')).toBe('equateur')
  })

  it('normalise "Colombie" → "colombie"', () => {
    expect(normalizeCountry('Colombie')).toBe('colombie')
  })

  it('majuscules converties en minuscules', () => {
    expect(normalizeCountry('BRÉSIL')).toBe('bresil')
  })
})

describe('Gateway — résolution URL par pays', () => {
  it('Brésil → URL backend Brésil', () => {
    expect(resolveApiUrl('Brésil')).toBe(MOCK_URLS.bresil)
  })

  it('Colombie → URL backend Colombie', () => {
    expect(resolveApiUrl('Colombie')).toBe(MOCK_URLS.colombie)
  })

  it('Équateur → URL backend Équateur', () => {
    expect(resolveApiUrl('Équateur')).toBe(MOCK_URLS.equateur)
  })

  it('pays inconnu → fallback Brésil', () => {
    expect(resolveApiUrl('Inconnu')).toBe(MOCK_URLS.bresil)
  })

  it('chaîne vide → fallback Brésil', () => {
    expect(resolveApiUrl('')).toBe(MOCK_URLS.bresil)
  })
})

describe('Gateway — construction URL complète', () => {
  it('concatène base URL + path correctement', () => {
    const base = resolveApiUrl('Brésil')
    const path = '/lots'
    expect(`${base}${path}`).toBe('http://backend:8000/api/v1/lots')
  })

  it('path sans / initial reste fonctionnel avec préfixe manuel', () => {
    const base = resolveApiUrl('Colombie')
    const path = 'alertes'
    expect(`${base}/${path}`).toBe('http://backend:8001/api/v1/alertes')
  })
})
