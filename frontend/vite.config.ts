import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'apple-touch-icon.png', 'masked-icon.svg'],
      manifest: {
        name: 'AURA — Beauty Intelligence Platform',
        short_name: 'AURA',
        description: 'Your AI-powered Beauty Passport',
        theme_color: '#C9A96E',
        background_color: '#0A0A0F',
        display: 'standalone',
        orientation: 'portrait',
        start_url: '/',
        icons: [
          { src: '/pwa-192x192.png', sizes: '192x192', type: 'image/png' },
          { src: '/pwa-512x512.png', sizes: '512x512', type: 'image/png' },
          { src: '/pwa-512x512.png', sizes: '512x512', type: 'image/png', purpose: 'any maskable' },
        ],
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
        runtimeCaching: [
          // Critical read-only data — CacheFirst, longer TTL
          {
            urlPattern: /\/api\/v1\/(sops|services|locations)\b/i,
            handler: 'CacheFirst',
            options: {
              cacheName: 'aura-static-data',
              expiration: { maxEntries: 100, maxAgeSeconds: 3600 }, // 1 hour
            },
          },
          // Today's bookings + customer profiles — NetworkFirst, short TTL
          {
            urlPattern: /\/api\/v1\/(bookings|customers|sessions|queue)\b/i,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'aura-live-data',
              expiration: { maxEntries: 200, maxAgeSeconds: 300 }, // 5 min
              networkTimeoutSeconds: 4,
            },
          },
          // Beauty Passport + consultation data — NetworkFirst
          {
            urlPattern: /\/api\/v1\/(customers\/.*\/passport|consultation|allergy|twin)\b/i,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'aura-passport-data',
              expiration: { maxEntries: 100, maxAgeSeconds: 600 }, // 10 min
              networkTimeoutSeconds: 4,
            },
          },
          // All other API calls — NetworkFirst, 5 min cache
          {
            urlPattern: /\/api\/v1\//i,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'aura-api-cache',
              expiration: { maxEntries: 100, maxAgeSeconds: 300 },
              networkTimeoutSeconds: 6,
            },
          },
          // Google Fonts + Maps tiles — CacheFirst
          {
            urlPattern: /^https:\/\/fonts\.googleapis\.com\//i,
            handler: 'CacheFirst',
            options: {
              cacheName: 'google-fonts',
              expiration: { maxEntries: 20, maxAgeSeconds: 86400 },
            },
          },
          {
            urlPattern: /^https:\/\/maps\.googleapis\.com\//i,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'google-maps',
              expiration: { maxEntries: 50, maxAgeSeconds: 300 },
            },
          },
        ],
      },
    }),
  ],
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules/react-dom') || id.includes('node_modules/react/') || id.includes('node_modules/react-router-dom')) {
            return 'vendor-react';
          }
          if (id.includes('node_modules/@tanstack/react-query')) {
            return 'vendor-query';
          }
          if (id.includes('node_modules/recharts')) {
            return 'vendor-charts';
          }
          if (id.includes('node_modules/framer-motion')) {
            return 'vendor-motion';
          }
          if (id.includes('node_modules/lucide-react')) {
            return 'vendor-icons';
          }
        },
      },
    },
  },
})
