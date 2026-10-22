# SITE — Astro pSEO directory

A static programmatic SEO directory built with Astro 4 + Tailwind CSS.

## What this is

- Predictive SEO (pSEO) directory site with programmatic routes per
  category and city.
- 10 demo listings across 3 categories × 5 cities at build time.
- CLS-safe ad slots, schema.org listing markup, and JSON-LD structured
  data on detail pages.
- robots.txt and sitemap.xml placeholders for the initial build.
- A Python scraper pipeline and a GitHub Actions daily refresh workflow
  that re-commits `src/data/listings.json`.

## Local development

```bash
npm install
npm run dev
```

Build:

```bash
npm run build
npm run preview
```

Output goes to `dist/`. Do not commit `dist/`.

## Repository layout

```text
/
├── astro.config.mjs
├── tailwind.config.mjs
├── package.json
├── package-lock.json
├── .gitignore
├── README.md
├── src/
│   ├── components/
│   │   ├── AdUnit.astro
│   │   ├── Header.astro
│   │   ├── Footer.astro
│   │   └── ListingCard.astro
│   ├── layouts/
│   │   └── Layout.astro
│   ├── pages/
│   │   ├── index.astro
│   │   └── [category]/[city]/
│   │       ├── index.astro
│   │       └── [slug].astro
│   ├── data/
│   │   └── listings.json
│   ├── types.ts
│   └── utils.ts
├── public/
│   ├── robots.txt
│   ├── sitemap.xml
│   └── favicon.svg
├── scripts/
│   ├── scraper.py
│   └── requirements.txt
└── site/          (local worker scaffolding; not shipped in the repo)
```

## Cloudflare Pages deployment

1. Push this repo to GitHub under your account.
2. In the Cloudflare Dashboard, go to **Workers & Pages** → **Create
   Application** → **Pages**.
3. Connect the GitHub repository.
4. Use these build settings:
   - Framework preset: **Astro**
   - Build command: `npm run build`
   - Build output directory: `dist`
5. Add the environment variable:
   - `NODE_VERSION = 20.0.0`
6. Save and deploy.

Before the first deploy, set your real domain in `astro.config.mjs`:

```js
export default defineConfig({
  site: "https://yourdomain.com",
  integrations: [sitemap(), tailwind()],
});
```

That makes `sitemap.xml` and canonical tags use absolute production URLs.

## Daily content refresh

`scripts/scraper.py` extracts listings and writes `src/data/listings.json`.
The GitHub Actions workflow in the deploy guide runs it on a daily cron and,
when data changes, commits the updated JSON back to the repository so Cloudflare
Pages rebuilds with fresh content.

The workflow file itself is intentionally kept out of this repo. Add it in the
repository that owns the Cloudflare Pages project, or wherever your CI runs.

## SEO notes

- Update `public/sitemap.xml` and `public/robots.txt` to match the live domain
  before launch.
- After deployment, submit the sitemap URL to Google Search Console.
- Ensure `site` in `astro.config.mjs` matches the canonical domain.

## Demo data

The initial `src/data/listings.json` contains 10 demo listings. Replace or
extend it with real scraped data before publishing.
