'use client';

// 다운로드 버튼 컴포넌트
// 생성된 학습 노트를 .md 파일로 다운로드하는 기능을 제공합니다.
export default function DownloadButton({ markdownContent, filename }) {
  const handleDownload = () => {
    // 마크다운 콘텐츠를 Blob 객체로 변환
    const blob = new Blob([markdownContent], { type: 'text/markdown;charset=utf-8' });

    // 다운로드 링크 생성
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;

    // 파일명 설정 (특수문자 제거 및 공백을 언더스코어로 변환)
    const safeFilename = filename
      ? filename.replace(/[^\w\s가-힣]/g, '').replace(/\s+/g, '_') + '.md'
      : '학습_노트.md';

    link.download = safeFilename;

    // 링크 클릭하여 다운로드 시작
    document.body.appendChild(link);
    link.click();

    // 링크 제거 및 URL 해제
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <button
      onClick={handleDownload}
      className="btn btn-primary w-full md:w-auto px-6 py-3 flex items-center justify-center dark:bg-blue-700 dark:hover:bg-blue-800"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        className="h-5 w-5 mr-2"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
        />
      </svg>
      노트 다운로드 (.md)
    </button>
  );
}