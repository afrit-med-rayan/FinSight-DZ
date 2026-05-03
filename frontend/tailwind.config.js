/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#e8f0fb',
          100: '#c5d5f5',
          500: '#185FA5',
          600: '#1450880',
          700: '#103d6e',
          900: '#07203c',
        },
        success: '#0F6E56',
        warning: '#BA7517',
        danger: '#A32D2D',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
