import type { NextConfig } from "next";

/**
 * Next.js configuration for GitHub Pages deployment
 * 
 * Key settings:
 * - output: 'export' enables static HTML export
 * - basePath: Set to your repository name (e.g., '/jec' for github.com/username/jec)
 * - images.unoptimized: Required for static export since GitHub Pages doesn't support Next.js Image Optimization
 */
const nextConfig: NextConfig = {
  // Enable static exports for GitHub Pages
  output: 'export',

  // Set the base path to your repository name
  // Change '/jec' to match your GitHub repository name
  // Leave as '' if deploying to username.github.io (user/org site)
  basePath: '/jec',

  // Disable image optimization for static export
  images: {
    unoptimized: true,
  },

  // Optional: Add trailing slashes to URLs
  trailingSlash: true,
};

export default nextConfig;
