/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      container: {
        center: true,
        padding: '1rem'
      }
    }
  },
  plugins: []
}