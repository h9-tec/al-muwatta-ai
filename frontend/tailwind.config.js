/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        islamic: {
          green: '#006B3F',
          gold: '#D4AF37',
          teal: '#008B8B',
          cream: '#F5F5DC',
          dark: '#1a1a1a',
        },
      },
      fontFamily: {
        arabic: ['Amiri', 'serif'],
        body: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}

