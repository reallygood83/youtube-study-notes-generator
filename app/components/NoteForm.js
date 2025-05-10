'use client';

import { useState } from 'react';
import axios from 'axios';
import LoadingSpinner from './LoadingSpinner';
import DownloadButton from './DownloadButton';

// 입력 타입 옵션
const INPUT_TYPES = {
  URL: 'url',
  TEXT: 'text'
};

// 노트 생성 폼 컴포넌트
export default function NoteForm() {
  // 상태 관리
  const [inputType, setInputType] = useState(INPUT_TYPES.URL);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState({
    success: false,
    markdownContent: '',
    videoTitle: '',
    error: null
  });
  
  // URL 유효성 검사 함수
  const isValidYoutubeUrl = (url) => {
    // 유튜브 URL 패턴 검사 (기본 유튜브 URL, 단축 URL 등 포함)
    const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+/;
    return youtubeRegex.test(url);
  };
  
  // 폼 제출 핸들러
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // 입력값 검증
    if (!inputValue.trim()) {
      alert(inputType === INPUT_TYPES.URL 
        ? '유튜브 URL을 입력해주세요.' 
        : '스크립트 텍스트를 입력해주세요.');
      return;
    }
    
    // URL 타입인 경우 유효성 추가 검사
    if (inputType === INPUT_TYPES.URL && !isValidYoutubeUrl(inputValue)) {
      alert('유효한 유튜브 URL을 입력해주세요.');
      return;
    }
    
    try {
      // 로딩 상태 시작
      setIsLoading(true);
      setResult({
        success: false,
        markdownContent: '',
        videoTitle: '',
        error: null
      });
      
      // API 호출
      const response = await axios.post('/api', {
        inputType,
        inputValue
      });
      
      // 결과 처리
      setResult({
        success: true,
        markdownContent: response.data.markdownContent,
        videoTitle: response.data.videoTitle || '유튜브_학습_노트',
        error: null
      });
    } catch (error) {
      // 오류 처리
      console.error('노트 생성 실패:', error);
      
      setResult({
        success: false,
        markdownContent: '',
        videoTitle: '',
        error: error.response?.data?.error || '노트 생성에 실패했습니다. 잠시 후 다시 시도해주세요.'
      });
    } finally {
      // 로딩 상태 종료
      setIsLoading(false);
    }
  };
  
  return (
    <div className="card">
      <h2 className="text-xl font-semibold mb-4">학습 노트 생성하기</h2>
      
      {/* 입력 타입 선택 */}
      <div className="flex mb-4 border rounded-md overflow-hidden">
        <button
          type="button"
          className={`flex-1 py-2 text-center transition ${
            inputType === INPUT_TYPES.URL 
              ? 'bg-blue-500 text-white' 
              : 'bg-gray-100 text-gray-700'
          }`}
          onClick={() => setInputType(INPUT_TYPES.URL)}
        >
          유튜브 URL
        </button>
        <button
          type="button"
          className={`flex-1 py-2 text-center transition ${
            inputType === INPUT_TYPES.TEXT 
              ? 'bg-blue-500 text-white' 
              : 'bg-gray-100 text-gray-700'
          }`}
          onClick={() => setInputType(INPUT_TYPES.TEXT)}
        >
          스크립트 직접 입력
        </button>
      </div>
      
      {/* 입력 폼 */}
      <form onSubmit={handleSubmit}>
        {inputType === INPUT_TYPES.URL ? (
          // URL 입력 필드
          <div className="mb-4">
            <label htmlFor="youtubeUrl" className="block mb-2 text-sm font-medium text-gray-600">
              유튜브 URL 주소
            </label>
            <input
              type="url"
              id="youtubeUrl"
              placeholder="https://www.youtube.com/watch?v=..."
              className="input"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              disabled={isLoading}
            />
          </div>
        ) : (
          // 텍스트 입력 필드
          <div className="mb-4">
            <label htmlFor="scriptText" className="block mb-2 text-sm font-medium text-gray-600">
              영상 스크립트 텍스트
            </label>
            <textarea
              id="scriptText"
              placeholder="영상의 스크립트나 대화 내용을 입력해주세요..."
              className="input min-h-[200px]"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              disabled={isLoading}
            />
          </div>
        )}
        
        {/* 제출 버튼 */}
        <button
          type="submit"
          className="btn btn-primary w-full"
          disabled={isLoading}
        >
          학습 노트 생성하기
        </button>
      </form>
      
      {/* 로딩 상태 표시 */}
      {isLoading && <LoadingSpinner />}
      
      {/* 결과 표시 */}
      {!isLoading && result.error && (
        <div className="mt-4 p-4 bg-red-100 text-red-700 rounded-md">
          <p className="font-medium">오류 발생</p>
          <p>{result.error}</p>
        </div>
      )}
      
      {!isLoading && result.success && (
        <div className="mt-6">
          <div className="mb-4 p-4 bg-green-100 text-green-700 rounded-md">
            <p className="font-medium">학습 노트 생성 완료!</p>
            <p>파일명: {result.videoTitle}_학습노트.md</p>
          </div>
          
          <div className="mb-4">
            <DownloadButton 
              markdownContent={result.markdownContent} 
              filename={`${result.videoTitle}_학습노트`}
            />
          </div>
          
          {/* 미리보기 */}
          <div className="mt-4">
            <h3 className="text-lg font-medium mb-2">노트 미리보기:</h3>
            <div className="p-4 bg-gray-50 rounded-md overflow-auto max-h-[300px] text-sm border">
              <pre className="whitespace-pre-wrap font-mono">{result.markdownContent}</pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}