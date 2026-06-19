import { H3Event } from 'h3'

export interface RegionalRequestOptions {
  method?: string
  body?: any
  query?: any
  headers?: Record<string, string>
}

export function getRegionalApiUrl(country: string): string {
  const config = useRuntimeConfig()
  const normalized = country.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "")

  if (normalized.includes('bresil')) {
    return config.apiBresilUrl
  } else if (normalized.includes('colombie')) {
    return config.apiColombieUrl
  } else if (normalized.includes('equateur')) {
    return config.apiEquateurUrl
  }

  return config.apiBresilUrl
}

export async function fetchFromCountry<T = any>(
  country: string,
  path: string,
  options: RegionalRequestOptions = {}
): Promise<T> {
  const baseUrl = getRegionalApiUrl(country)
  const cleanPath = path.startsWith('/') ? path : `/${path}`
  const targetUrl = `${baseUrl}${cleanPath}`

  try {
    const response = await $fetch<T>(targetUrl, {
      method: options.method || 'GET',
      body: options.body,
      query: options.query,
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {})
      }
    })

    if (Array.isArray(response)) {
      return response.map(item => ({
        nom_pays: country,
        ...item,
        node_pays: country,
        online: true
      })) as unknown as T
    }

    if (response && typeof response === 'object') {
      return {
        nom_pays: country,
        ...response,
        node_pays: country,
        online: true
      } as unknown as T
    }

    return response
  } catch (err: any) {
    console.log(`[Gateway Warning] Node ${country} is offline (${targetUrl}). Using fallback values.`)

    if (options.method === 'GET' || !options.method) {
      if (path.includes('/configuration-pays')) {
        try {
          const bresilUrl = getRegionalApiUrl('Brésil')
          const backupUrl = `${bresilUrl}/configuration-pays/${country}`
          const backupConfig = await $fetch<any>(backupUrl)
          if (backupConfig) {
            return {
              ...backupConfig,
              nom_pays: country,
              node_pays: country,
              online: false
            } as unknown as T
          }
        } catch (backupErr) {
          // ignore backup errors and fallback to static defaults
        }

        return {
          nom_pays: country,
          node_pays: country,
          email_responsable: `exploitation.${country.toLowerCase()}@futurekawa.com`,
          temp_ideale: country === 'Colombie' ? 26.0 : country === 'Équateur' ? 31.0 : 29.0,
          hum_ideale: country === 'Colombie' ? 80.0 : country === 'Équateur' ? 60.0 : 55.0,
          tolerance_temp: 3.0,
          tolerance_hum: 2.0,
          online: false
        } as unknown as T
      }

      const isSingleItem = path.match(/\/(lots|entrepots|modules|releves|alertes)\/[^/]+$/)
      if (isSingleItem) {
        return null as unknown as T
      }

      return [] as unknown as T
    }

    throw err
  }
}

export async function fetchFromAllCountries<T = any>(
  path: string,
  options: RegionalRequestOptions = {}
): Promise<T[]> {
  const countries = ['Brésil', 'Colombie', 'Équateur']

  const promises = countries.map(async (country) => {
    try {
      const data = await fetchFromCountry(country, path, options)
      return Array.isArray(data) ? data : [data]
    } catch (err) {
      console.warn(`[Gateway Warning] Skipping country ${country} due to error.`)
      return []
    }
  })

  const results = await Promise.all(promises)
  return results.flat() as T[]
}

export function getCountryFromEvent(event: H3Event): string {
  const query = getQuery(event)
  if (query.pays) return String(query.pays)
  if (query.country) return String(query.country)

  const headerPays = getHeader(event, 'x-country') || getHeader(event, 'X-Country')
  if (headerPays) return decodeURIComponent(headerPays)

  return 'Brésil'
}
