'use client';

// 로딩 스피너 컴포넌트
// 노트 생성 중일 때 사용자에게 작업이 진행 중임을 시각적으로 표시합니다.
export default function LoadingSpinner() {
  return (
    <div className="flex flex-col items-center justify-center my-8">
      <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-blue-500"></div>
      <p className="mt-4 text-gray-600">학습 노트를 생성하고 있습니다. 잠시만 기다려주세요...</p>
      <p className="text-sm text-gray-500 mt-2">
        (영상 길이에 따라 30초~2분 정도 소요될 수 있습니다)
      </p>
    </div>
  );
}