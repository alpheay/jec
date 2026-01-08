# GitHub Pages Setup Guide for JEC Docs

This guide will help you deploy your Next.js documentation site to GitHub Pages.

## Prerequisites

- A GitHub repository (already set up: `jec`)
- Git installed locally
- Node.js and npm installed

## Step 1: Enable GitHub Pages

1. Go to your GitHub repository: `https://github.com/YOUR_USERNAME/jec`
2. Click on **Settings** tab
3. In the left sidebar, click **Pages**
4. Under **Source**, select **GitHub Actions**

## Step 2: Update Configuration (if needed)

The Next.js app is already configured for GitHub Pages in `docs/next.config.ts`:

```typescript
basePath: '/jec',  // This should match your repository name
```

**Important:** 
- If your repository name is different from `jec`, update the `basePath` in `docs/next.config.ts`
- If deploying to a user/organization site (e.g., `username.github.io`), set `basePath: ''`

## Step 3: Commit and Push

```bash
# Add all files
git add .

# Commit changes
git commit -m "Add Next.js documentation site"

# Push to GitHub
git push origin main
```

## Step 4: Monitor Deployment

1. Go to the **Actions** tab in your GitHub repository
2. You should see the "Deploy Next.js Docs to GitHub Pages" workflow running
3. Wait for it to complete (usually takes 2-3 minutes)
4. Once complete, your site will be available at: `https://YOUR_USERNAME.github.io/jec/`

## Local Development

```bash
# Navigate to docs directory
cd docs

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

Visit `http://localhost:3000/jec` to see your site locally.

## Building Locally

To test the production build locally:

```bash
cd docs
npm run build
```

The static files will be generated in the `docs/out` directory.

## Troubleshooting

### 404 Error on GitHub Pages

- Verify that GitHub Pages is enabled in repository settings
- Check that the workflow completed successfully in the Actions tab
- Ensure the `basePath` in `next.config.ts` matches your repository name

### Images Not Loading

- Make sure images are in the `docs/public` directory
- Use relative paths: `/jec/image.png` (including the base path)
- Or use Next.js Image component with `unoptimized` prop

### Workflow Fails

- Check the Actions tab for error messages
- Ensure `package-lock.json` is committed
- Verify Node.js version compatibility

## Customizing Your Docs

Edit the files in `docs/src/app` to customize your documentation:

- `docs/src/app/page.tsx` - Home page
- `docs/src/app/layout.tsx` - Root layout (metadata, fonts, etc.)
- `docs/src/app/globals.css` - Global styles

## Next Steps

1. Customize the home page in `docs/src/app/page.tsx`
2. Add more pages by creating new directories/files in `docs/src/app`
3. Update metadata in `docs/src/app/layout.tsx`
4. Add your API documentation content
5. Customize styling in `docs/src/app/globals.css` or with Tailwind classes

## Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [Next.js Static Exports](https://nextjs.org/docs/app/building-your-application/deploying/static-exports)
