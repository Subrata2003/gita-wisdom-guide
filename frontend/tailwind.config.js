/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        saffron: '#FF8C00',
        'saffron-light': '#FFA533',
        'saffron-dark': '#CC7000',
        gold: '#FFD700',
        'gold-dark': '#B8860B',
        midnight: '#0D0B1E',
        'midnight-100': '#1A1640',
        'midnight-200': '#221E52',
        'midnight-300': '#2D2868',
        'midnight-400': '#3D3880',
        cream: '#F5E6C8',
        'cream-dark': '#B8A48C',
        'text-muted': '#7B6FA0',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'spin-slow': 'spin 80s linear infinite',
        'pulse-soft': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float': 'float 6s ease-in-out infinite',
        'fade-up': 'fadeUp 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards',
        'typing': 'typing 1.4s ease-in-out infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-8px)' },
        },
        fadeUp: {
          from: { opacity: '0', transform: 'translateY(16px) scale(0.97)' },
          to: { opacity: '1', transform: 'translateY(0) scale(1)' },
        },
        typing: {
          '0%, 60%, 100%': { opacity: '0.2', transform: 'scale(0.8)' },
          '30%': { opacity: '1', transform: 'scale(1)' },
        },
      },
      boxShadow: {
        saffron: '0 4px 24px rgba(255, 140, 0, 0.25)',
        'saffron-lg': '0 8px 40px rgba(255, 140, 0, 0.35)',
        card: '0 4px 24px rgba(0, 0, 0, 0.4)',
      },
    },
  },
  plugins: [],
}
