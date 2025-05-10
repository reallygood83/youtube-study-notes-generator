import './globals.css'

export const metadata = {
  title: '유튜브 스터디 노트 제너레이터',
  description: '유튜브 콘텐츠 기반으로 구조화된 학습 노트를 생성하는 서비스',
}

export default function RootLayout({ children }) {
  return (
    <html lang="ko">
      <body>
        <main className="min-h-screen bg-gray-100 dark:bg-gray-900 transition-colors duration-200">
          {children}
        </main>
      </body>
    </html>
  )
}