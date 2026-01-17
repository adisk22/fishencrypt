/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        carbon: {
          950: '#050505',
          900: '#0a0a0a',
          800: '#141414',
          700: '#1a1a1a',
          600: '#262626',
        },
        neon: {
          purple: '#b026ff',
          'purple-light': '#c084fc',
          'purple-dim': '#7c3aed',
        },
      },
      boxShadow: {
        'neon': '0 0 20px rgba(176,38,255,0.4)',
        'neon-lg': '0 0 30px rgba(176,38,255,0.6)',
      },
    },
  },
  plugins: [],
}

