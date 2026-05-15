/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Cores do Design System do Governo Federal
        'gov': {
          'green': '#06C637',
          'blue': '#006294',
          'red': '#D64040',
          'yellow': '#F5A623',
          'gray': '#9B9B9B',
          'light-gray': '#F5F5F5',
          'dark-gray': '#4A4A4A',
        }
      },
      fontFamily: {
        sans: ['system-ui', 'Segoe UI', 'Roboto', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
