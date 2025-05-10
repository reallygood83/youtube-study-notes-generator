'use client';

import NoteForm from './components/NoteForm';

export default function Home() {
  return (
    <div className="container mx-auto px-4 py-8">
      <header className="text-center mb-8">
        <h1 className="text-3xl font-bold mb-2 dark:text-white">유튜브 스터디 노트 제너레이터</h1>
        <p className="text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
          유튜브 비디오 링크를 입력하면 AI가 영상 콘텐츠를 분석하여 구조화된 학습 노트를 자동으로 생성해 드립니다.
          생성된 노트는 Markdown(.md) 파일로 다운로드 받을 수 있습니다.
        </p>
      </header>

      <section className="max-w-3xl mx-auto">
        <div className="bg-blue-50 dark:bg-blue-900/30 p-4 rounded-lg mb-6 border border-blue-200 dark:border-blue-800">
          <h2 className="text-lg font-medium text-blue-800 dark:text-blue-300 mb-2">사용 방법</h2>
          <ol className="list-decimal list-inside text-blue-700 dark:text-blue-300 space-y-1">
            <li>아래 입력란에 <strong>유튜브 URL</strong>을 붙여넣거나, 스크립트를 직접 입력하세요.</li>
            <li>&quot;학습 노트 생성하기&quot; 버튼을 클릭하세요.</li>
            <li>초보자용/고급자용 학습 노트 형식을 선택하세요.</li>
            <li>생성 완료 후 &quot;노트 다운로드&quot; 버튼을 클릭하여 Markdown 파일을 저장하세요.</li>
            <li>클립보드 복사 기능으로 쉽게 노트를 다른 앱에 붙여넣을 수 있습니다.</li>
            <li>다운로드한 파일은 Obsidian, Notion 등 마크다운을 지원하는 도구에서 열어볼 수 있습니다.</li>
          </ol>
        </div>

        <NoteForm />

        <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg mt-8 border border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-medium dark:text-gray-200 mb-2">유튜브 스터디 노트 제너레이터 소개</h2>
          <div className="text-gray-600 dark:text-gray-300 space-y-2">
            <p>
              이 서비스는 유튜브 교육 콘텐츠를 효과적으로 학습하기 위한 도구입니다.
              영상의 자막을 AI가 분석하여 핵심 개념, 구조화된 내용, 자기평가 질문이 포함된 마크다운 노트를 생성합니다.
            </p>
            <p>
              공부의 효율성을 높이고, 교육 콘텐츠를 체계적으로 정리하여 지식을 확장하세요!
            </p>
            <p>
              <strong>특징:</strong> 자막 자동 추출, 구조화된 학습 노트, 커스텀 학습 레벨, 다크 모드 지원, 노트 히스토리 저장
            </p>
          </div>
        </div>

        <footer className="mt-8 text-center text-sm text-gray-500 dark:text-gray-400">
          <p>© 2025 유튜브 스터디 노트 제너레이터 | Created by 배움의 달인</p>
          <p className="mt-1">
            <a href="https://www.youtube.com/@learningmaster" target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">
              YouTube 채널 방문하기
            </a>
          </p>
        </footer>
      </section>
    </div>
  );
}