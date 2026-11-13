/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#eef4ff', 100: '#dbe6fe', 200: '#bfd3fe', 500: '#3b6cf6', 600: '#2553eb',
          700: '#1d43d8', 800: '#1e38af', 900: '#1e348a', 950: '#172254',
        },
        accent: { 400: '#fbbf24', 500: '#f59e0b' },
      },
      fontFamily: { sans: ['Inter', 'system-ui', 'sans-serif'] },
    },
  },
  plugins: [],
}
