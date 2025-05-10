/** @type {import('next').NextConfig} */
const nextConfig = {
  // API 설정
  rewrites: async () => {
    return [
      {
        source: '/api',
        destination: '/api/index.py',
      },
      {
        source: '/api/:path*',
        destination: '/api/:path*',
      },
    ];
  },
  // 서버 설정
  serverRuntimeConfig: {
    PROJECT_ROOT: __dirname,
  },
  // 국제화 설정
  i18n: {
    locales: ['ko'],
    defaultLocale: 'ko',
  },
  // 이미지 최적화 설정
  images: {
    domains: ['i.ytimg.com', 'img.youtube.com'],
  },
}

module.exports = nextConfig