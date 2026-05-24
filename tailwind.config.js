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
        // gov-green escurecido para atingir razão de contraste ≥ 4.5:1 sobre branco (WCAG 1.4.3 AA)
        // #06C637 original = 2.28:1 (falha); #1a7a2e = ~5.0:1 (aprovado)
        'gov': {
          'green': '#1a7a2e',
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
