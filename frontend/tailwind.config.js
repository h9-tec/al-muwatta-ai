/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Prophetic theme - sophisticated and meaningful
        prophetic: {
          white: '#FDFCFA',
          cream: '#F5F3F0',
          ivory: '#EBE8E3',
        },
        paradise: {
          50: '#E8F5F2',
          100: '#C7E7E1',
          200: '#9DD9CE',
          300: '#6DCBBB',
          400: '#41B8A6',
          500: '#0D7C66', // Main paradise green
          600: '#0A6655',
          700: '#085243',
          800: #053D32',
          900: '#032920',
        },
        earth: {
          brown: '#6B5B4C',
          sand: '#C9B8A3',
          clay: '#A08974',
        },
        // Semantic colors (muted, professional)
        quranic: '#1E40AF',
        hadith: '#92400E',
        fiqh: '#0D7C66',
      },
      fontFamily: {
        arabic: ['Amiri', 'Noto Naskh Arabic', 'Traditional Arabic', 'serif'],
        body: ['Inter', 'system-ui', 'sans-serif'],
        heading: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'prophetic-sm': '0 2px 8px rgba(13, 124, 102, 0.08)',
        'prophetic': '0 4px 16px rgba(13, 124, 102, 0.12)',
        'prophetic-lg': '0 8px 32px rgba(13, 124, 102, 0.16)',
      },
      backgroundImage: {
        'gradient-paradise': 'linear-gradient(135deg, #0D7C66 0%, #41B8A6 100%)',
        'gradient-prophetic': 'linear-gradient(135deg, #F5F3F0 0%, #FDFCFA 100%)',
        'gradient-earth': 'linear-gradient(135deg, #A08974 0%, #C9B8A3 100%)',
      },
    },
  },
  plugins: [],
}
