import { defineConfig } from 'astro/config';
// sitemap generation handled via static public/sitemap.xml + robots.txt
// import sitemap from '@astrojs/sitemap';
import tailwind from '@astrojs/tailwind';

export default defineConfig({
  site: 'https://example.com',
  output: 'static',
  trailingSlash: 'always',
  integrations: [
    // sitemap() — disabled: use public/sitemap.xml instead
    tailwind(),
  ],
  vite: {
    build: {
      cssMinify: true,
      sourcemap: false,
    },
  },
  build: {
    assets: '_assets',
  },
  experimental: {
    clientPrerender: false,
  },
  adapter: undefined,
});
