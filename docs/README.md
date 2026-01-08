# JEC API Documentation

This is the documentation site for the JEC API, built with Next.js and deployed to GitHub Pages.

## Development

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

Open [http://localhost:3000/jec](http://localhost:3000/jec) in your browser.

## Building for Production

```bash
# Build static site
npm run build

# The output will be in the 'out' directory
```

## Deployment

This site is automatically deployed to GitHub Pages when changes are pushed to the main branch.

The deployment is handled by the GitHub Actions workflow at `.github/workflows/deploy-docs.yml`.

## Configuration

The site is configured for GitHub Pages in `next.config.ts`:
- Static export enabled
- Base path set to `/jec` (repository name)
- Image optimization disabled for static hosting

## Project Structure

```
docs/
├── src/
│   └── app/          # App Router pages
├── public/           # Static assets
├── next.config.ts    # Next.js configuration
└── package.json      # Dependencies
```
