# Next.js GitHub Pages - Quick Reference

## 📁 What Was Created

```
jec/
├── .github/
│   └── workflows/
│       └── deploy-docs.yml          # Auto-deployment workflow
├── docs/                             # Next.js application
│   ├── src/
│   │   └── app/                      # Your pages go here
│   ├── public/
│   │   └── .nojekyll                 # Prevents Jekyll processing
│   ├── next.config.ts                # Configured for GitHub Pages
│   ├── package.json
│   ├── README.md                     # Docs README
│   └── GITHUB_PAGES_SETUP.md         # Setup instructions
└── .gitignore                        # Updated with Next.js ignores
```

## 🚀 Quick Start

### Local Development
```bash
cd docs
npm install
npm run dev
```
Visit: `http://localhost:3000/jec`

### Deploy to GitHub Pages
```bash
git add .
git commit -m "Add Next.js docs"
git push origin main
```

Your site will be live at: `https://YOUR_USERNAME.github.io/jec/`

## ⚙️ Configuration

### Key Settings in `next.config.ts`
- ✅ `output: 'export'` - Static export enabled
- ✅ `basePath: '/jec'` - Matches repository name
- ✅ `images.unoptimized: true` - Required for static hosting
- ✅ `trailingSlash: true` - Better compatibility

### GitHub Repository Settings
1. Go to **Settings** → **Pages**
2. Set **Source** to **GitHub Actions**

## 📝 Customization

### Edit Home Page
`docs/src/app/page.tsx`

### Add New Pages
Create files in `docs/src/app/`:
- `docs/src/app/about/page.tsx` → `/jec/about`
- `docs/src/app/api/page.tsx` → `/jec/api`

### Update Metadata
`docs/src/app/layout.tsx`

### Styling
- Global CSS: `docs/src/app/globals.css`
- Tailwind: Use utility classes in components

## 🔧 Important Notes

### Base Path
- **Repository site** (e.g., `username.github.io/jec`): Use `basePath: '/jec'`
- **User/Org site** (e.g., `username.github.io`): Use `basePath: ''`

### Images
Place in `docs/public/` and reference with base path:
```tsx
<img src="/jec/logo.png" alt="Logo" />
```

### Links
Use Next.js Link component:
```tsx
import Link from 'next/link';

<Link href="/about">About</Link>  // basePath added automatically
```

## 🐛 Troubleshooting

### Build fails locally
```bash
cd docs
rm -rf .next node_modules package-lock.json
npm install
npm run build
```

### 404 on GitHub Pages
- Check Actions tab for deployment status
- Verify basePath matches repository name
- Ensure GitHub Pages source is set to "GitHub Actions"

### Styles not loading
- Clear browser cache
- Check browser console for errors
- Verify basePath is correct

## 📚 Resources

- [Full Setup Guide](./docs/GITHUB_PAGES_SETUP.md)
- [Next.js Docs](https://nextjs.org/docs)
- [Static Exports](https://nextjs.org/docs/app/building-your-application/deploying/static-exports)
