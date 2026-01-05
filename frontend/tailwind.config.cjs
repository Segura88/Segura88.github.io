module.exports = {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: { extend: {} },
  plugins: [require('daisyui')],
  daisyui: {
    themes: [
      {
        memories: {
          primary: '#2563eb',
          secondary: '#7c3aed',
          accent: '#06b6d4',
          neutral: '#111827',
          'base-100': '#ffffff'
        }
      }
    ]
  }
}
