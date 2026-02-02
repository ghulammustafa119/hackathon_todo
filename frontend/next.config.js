/** @type {import('next').NextConfig} */
const nextConfig = {
  /* config options here */
  // Remove static export to allow middleware
  // output: 'export',  // Commented out to allow dynamic features like middleware
  trailingSlash: false,
};

module.exports = nextConfig;