import type { NextConfig } from "next";

/**
 * Next.js configuration for GitHub Pages deployment
 * 
 * Key settings:
 * - output: 'export' enables static HTML export
 * - basePath: Set to your repository name for production (e.g., '/jec' for github.com/username/jec)
 * - images.unoptimized: Required for static export since GitHub Pages doesn't support Next.js Image Optimization
 */

const isProd = process.env.NODE_ENV === 'production';

const nextConfig: NextConfig = {
  // Enable static exports for GitHub Pages
  output: 'export',

  // Set the base path to your repository name for production only
  // For local development, we use no base path
  basePath: isProd ? '/jec' : '',

  // Disable image optimization for static export
  images: {
    unoptimized: true,
  },

  // Optional: Add trailing slashes to URLs
  trailingSlash: true,
};

export default nextConfig;
