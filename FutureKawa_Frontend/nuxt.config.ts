export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },

  app: {
    head: {
      title: 'FutureKawa - Hub Industriel',
      meta: [
        { name: 'description', content: 'Console de supervision industrielle et traçabilité du café' }
      ],
      link: [
        { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Share+Tech+Mono&display=swap' }
      ]
    }
  },

  css: [
    '~/assets/css/main.css'
  ],

  runtimeConfig: {
    apiBresilUrl: process.env.API_BRESIL_URL || 'http://localhost:8000/api/v1',
    apiColombieUrl: process.env.API_COLOMBIE_URL || 'http://localhost:8001/api/v1',
    apiEquateurUrl: process.env.API_EQUATEUR_URL || 'http://localhost:8002/api/v1',
  }
})
