/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_URL: 'http://localhost:8000',
    NEXT_PUBLIC_API_URL_SERVER: process.env.NEXT_PUBLIC_API_URL || 'http://backend:8000',
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `http://backend:8000/api/:path*`,
      },
    ]
  },
}

module.exports = nextConfig