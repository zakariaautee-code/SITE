/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        ink: '#131816',
        'ink-2': '#2C3531',
        muted: '#6B7770',
        line: '#E2E7E3',
        paper: '#F2F5F3',
        card: '#FFFFFF',
        accent: '#E4A11B',
        hot: '#D24B2E',
        booked: '#1E7A5B',
        warm: '#B98412',
        cold: '#8A9490',
        'wa-header': '#075E54',
        'wa-teal': '#128C7E',
        'wa-out': '#DCF8C6',
        'wa-bg': '#ECE5DD',
      },
      fontFamily: {
        display: ['var(--font-display)'],
        body: ['var(--font-body)'],
      },
      fontSize: {
        '2xs': ['0.625rem', { lineHeight: '1rem' }],
      },
    },
  },
  plugins: [],
  important: 'body',
};
