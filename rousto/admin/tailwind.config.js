/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './**/*.{html,js}',
    '../web/**/*.{html,js}',
  ],
  theme: {
    extend: {
      colors: {
        'brand-red': {
          DEFAULT: '#C1121F',
          50: '#FCE8EA',
          600: '#9A0E18',
          700: '#7A0B13',
        },
        'brand-navy': {
          DEFAULT: '#003049',
          50: '#E8EEF2',
          light: '#1A5578',
        },
        'brand-bg': '#F8F9FA',
        'brand-line': '#E8ECF0',
      },
      fontFamily: {
        ar: ['Tajawal', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        brand: '14px',
      },
      boxShadow: {
        'brand-sm': '0 6px 20px rgba(0, 48, 73, 0.06)',
        'brand-md': '0 10px 28px rgba(0, 48, 73, 0.10)',
        'brand-focus-navy': '0 0 0 3px rgba(0, 48, 73, 0.12)',
        'brand-focus-red': '0 0 0 3px rgba(193, 18, 31, 0.14)',
      },
    },
  },
  plugins: [],
};
