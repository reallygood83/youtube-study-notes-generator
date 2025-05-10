/** @type {import('next').NextConfig} */
const nextConfig = {
  // Python API ���x� $
  rewrites: async () => {
    return [
      {
        source: '/api/:path*',
        destination: '/api/:path*',
      },
    ];
  },
  // ��� h $
  serverRuntimeConfig: {
    PROJECT_ROOT: __dirname,
  },
}

module.exports = nextConfig