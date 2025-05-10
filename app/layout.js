import './globals.css'

export const metadata = {
  title: ' � �0 x� t0',
  description: ' � D$X ��D �<\ lpT Y� x�| �1X� D�',
}

export default function RootLayout({ children }) {
  return (
    <html lang="ko">
      <body>
        <main className="min-h-screen bg-gray-100">
          {children}
        </main>
      </body>
    </html>
  )
}