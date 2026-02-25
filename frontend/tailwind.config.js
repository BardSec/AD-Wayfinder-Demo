/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        domain: {
          DEFAULT: '#4f46e5',
          light: '#e0e7ff',
          dark: '#3730a3',
        },
        ou: {
          DEFAULT: '#d97706',
          light: '#fef3c7',
          dark: '#b45309',
        },
        group: {
          DEFAULT: '#059669',
          light: '#d1fae5',
          dark: '#047857',
        },
        alert: {
          DEFAULT: '#dc2626',
          light: '#fee2e2',
          dark: '#b91c1c',
        },
      },
    },
  },
  plugins: [],
}
