module.exports = {
  content: [
    "./wmsr/templates/**/*.html",
    "./wmsr/**/*.py"
  ],
  safelist: [
    'cursor-pointer',
    'cursor-not-allowed',
    'file:cursor-pointer',
    'file:bg-transparent',
    'file:border-none'
    // agrega aquí otras clases que uses dinámicamente
  ],
  theme: { extend: {} },
  plugins: []
}