'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import LoadingSpinner from './LoadingSpinner';
import DownloadButton from './DownloadButton';

// 입력 타입 옵션
const INPUT_TYPES = {
  URL: 'url',
  TEXT: 'text'
};

// 학습 수준 옵션
const LEARNING_LEVELS = {
  BEGINNER: 'beginner',
  ADVANCED: 'advanced'
};

// 노트 생성 폼 컴포넌트
export default function NoteForm() {
  // 상태 관리
  const [inputType, setInputType] = useState(INPUT_TYPES.URL);
  const [inputValue, setInputValue] = useState('');
  const [learningLevel, setLearningLevel] = useState(LEARNING_LEVELS.BEGINNER);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState({
    success: false,
    markdownContent: '',
    videoTitle: '',
    error: null
  });
  const [history, setHistory] = useState([]);
  const [isDarkMode, setIsDarkMode] = useState(false);

  // 컴포넌트 마운트 시 로컬 스토리지에서 히스토리와 다크모드 설정 불러오기
  useEffect(() => {
    // 히스토리 불러오기
    const savedHistory = localStorage.getItem('noteHistory');
    if (savedHistory) {
      try {
        setHistory(JSON.parse(savedHistory));
      } catch (e) {
        console.error('히스토리 파싱 오류:', e);
      }
    }

    // 다크모드 설정 불러오기
    const darkModeSetting = localStorage.getItem('darkMode') === 'true';
    setIsDarkMode(darkModeSetting);

    // 다크모드 적용
    if (darkModeSetting) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, []);

  // 다크모드 토글 함수
  const toggleDarkMode = () => {
    const newDarkMode = !isDarkMode;
    setIsDarkMode(newDarkMode);
    localStorage.setItem('darkMode', newDarkMode.toString());

    if (newDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };
  
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
        inputValue,
        learningLevel
      });
      
      // 결과 처리
      const newResult = {
        success: true,
        markdownContent: response.data.markdownContent,
        videoTitle: response.data.videoTitle || '유튜브_학습_노트',
        error: null,
        timestamp: new Date().toISOString(),
        inputType,
        inputValue: inputType === INPUT_TYPES.URL ? inputValue : inputValue.substring(0, 100) + '...',
        learningLevel
      };

      setResult(newResult);

      // 히스토리에 추가
      const newHistory = [newResult, ...history].slice(0, 10); // 최대 10개 저장
      setHistory(newHistory);
      localStorage.setItem('noteHistory', JSON.stringify(newHistory));
    } catch (error) {
      // 오류 처리
      console.error('노트 생성 실패:', error);

      // API 응답에서 오류 정보 추출
      const errorResponse = error.response?.data || {};
      const errorMessage = errorResponse.error || '노트 생성에 실패했습니다. 잠시 후 다시 시도해주세요.';
      const errorType = errorResponse.errorType || 'UNKNOWN_ERROR';
      const recommendationText = errorResponse.recommendationText || '';
      const helpText = errorResponse.helpText || '';

      setResult({
        success: false,
        markdownContent: '',
        videoTitle: '',
        error: errorMessage,
        errorType: errorType,
        recommendationText: recommendationText,
        helpText: helpText
      });
    } finally {
      // 로딩 상태 종료
      setIsLoading(false);
    }
  };
  
  // 클립보드에 복사 함수
  const copyToClipboard = () => {
    if (!result.markdownContent) return;

    navigator.clipboard.writeText(result.markdownContent)
      .then(() => {
        alert('클립보드에 복사되었습니다!');
      })
      .catch(err => {
        console.error('클립보드 복사 실패:', err);
        alert('클립보드 복사에 실패했습니다.');
      });
  };

  // 히스토리에서 노트 불러오기
  const loadFromHistory = (item) => {
    setResult({
      success: true,
      markdownContent: item.markdownContent,
      videoTitle: item.videoTitle,
      error: null
    });
  };

  return (
    <div className={`card ${isDarkMode ? 'dark-card' : ''}`}>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">학습 노트 생성하기</h2>
        <button
          onClick={toggleDarkMode}
          className="p-2 rounded-full text-gray-600 hover:bg-gray-200 dark:text-gray-300 dark:hover:bg-gray-700"
          aria-label="Toggle dark mode"
        >
          {isDarkMode ? (
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clipRule="evenodd" />
            </svg>
          ) : (
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
            </svg>
          )}
        </button>
      </div>
      
      {/* 입력 타입 선택 */}
      <div className="flex mb-4 border rounded-md overflow-hidden dark:border-gray-700">
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
        
        {/* 학습 레벨 선택 */}
        <div className="mb-4">
          <label className="block mb-2 text-sm font-medium text-gray-600 dark:text-gray-300">
            학습 노트 형식
          </label>
          <div className="flex border rounded-md overflow-hidden dark:border-gray-700">
            <button
              type="button"
              className={`flex-1 py-2 text-center transition ${
                learningLevel === LEARNING_LEVELS.BEGINNER
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300'
              }`}
              onClick={() => setLearningLevel(LEARNING_LEVELS.BEGINNER)}
            >
              초보자용
            </button>
            <button
              type="button"
              className={`flex-1 py-2 text-center transition ${
                learningLevel === LEARNING_LEVELS.ADVANCED
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300'
              }`}
              onClick={() => setLearningLevel(LEARNING_LEVELS.ADVANCED)}
            >
              고급자용
            </button>
          </div>
          <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
            초보자용: 기본 개념 설명과 쉬운 예시가 포함됩니다.<br />
            고급자용: 더 깊이 있는 내용과 응용 방법이 포함됩니다.
          </p>
        </div>

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
      
      {/* 히스토리 표시 */}
      {history.length > 0 && !result.success && !isLoading && !result.error && (
        <div className="mt-6">
          <h3 className="text-lg font-medium mb-2 dark:text-gray-200">이전 생성 기록:</h3>
          <div className="space-y-2">
            {history.map((item, index) => (
              <div key={index} className="p-3 bg-gray-50 dark:bg-gray-800 rounded-md border dark:border-gray-700 flex justify-between items-center">
                <div>
                  <p className="font-medium dark:text-gray-200">{item.videoTitle}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {new Date(item.timestamp).toLocaleString()} ·
                    {item.inputType === INPUT_TYPES.URL ? '유튜브 URL' : '스크립트'} ·
                    {item.learningLevel === LEARNING_LEVELS.BEGINNER ? '초보자용' : '고급자용'}
                  </p>
                </div>
                <button
                  onClick={() => loadFromHistory(item)}
                  className="btn btn-secondary text-sm px-3 py-1 dark:bg-gray-700 dark:text-gray-300"
                >
                  불러오기
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 오류 표시 */}
      {!isLoading && result.error && (
        <div className="mt-4 p-4 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 rounded-md">
          <p className="font-medium">오류 발생</p>
          <p>{result.error}</p>

          {/* 추천 해결책 표시 */}
          {result.recommendationText && (
            <div className="mt-2 text-sm">
              <p className="font-medium">권장 해결 방법:</p>
              <p>{result.recommendationText}</p>
            </div>
          )}

          {/* 도움말 텍스트 표시 */}
          {result.helpText && (
            <div className="mt-2 text-sm italic">
              <p>{result.helpText}</p>
            </div>
          )}

          {/* 자막 문제인 경우 입력 모드 전환 버튼 표시 */}
          {(result.errorType === 'TRANSCRIPTS_DISABLED' ||
            result.errorType === 'NO_TRANSCRIPT' ||
            result.errorType === 'TRANSCRIPT_ERROR') && (
            <button
              onClick={() => setInputType(INPUT_TYPES.TEXT)}
              className="mt-3 bg-white dark:bg-gray-800 text-red-600 dark:text-red-400 px-3 py-1 rounded-md text-sm shadow-sm hover:bg-gray-100 dark:hover:bg-gray-700"
            >
              스크립트 직접 입력 모드로 전환
            </button>
          )}
        </div>
      )}

      {!isLoading && result.success && (
        <div className="mt-6">
          <div className="mb-4 p-4 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 rounded-md">
            <p className="font-medium">학습 노트 생성 완료!</p>
            <p>파일명: {result.videoTitle}_학습노트.md</p>
          </div>

          <div className="mb-4 flex flex-wrap gap-2">
            <DownloadButton
              markdownContent={result.markdownContent}
              filename={`${result.videoTitle}_학습노트`}
            />

            <button
              onClick={copyToClipboard}
              className="btn btn-secondary px-4 py-2 flex items-center dark:bg-gray-700 dark:text-gray-300"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                <path d="M8 3a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z" />
                <path d="M6 3a2 2 0 00-2 2v11a2 2 0 002 2h8a2 2 0 002-2V5a2 2 0 00-2-2 3 3 0 01-3 3H9a3 3 0 01-3-3z" />
              </svg>
              클립보드에 복사
            </button>

            <button
              onClick={() => {
                if (navigator.share) {
                  navigator.share({
                    title: `${result.videoTitle} - 학습 노트`,
                    text: result.markdownContent,
                    url: window.location.href
                  }).catch(err => console.error('공유 실패:', err));
                } else {
                  alert('이 브라우저에서는 공유 기능을 지원하지 않습니다.');
                }
              }}
              className="btn btn-secondary px-4 py-2 flex items-center dark:bg-gray-700 dark:text-gray-300"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                <path d="M15 8a3 3 0 10-2.977-2.63l-4.94 2.47a3 3 0 100 4.319l4.94 2.47a3 3 0 10.895-1.789l-4.94-2.47a3.027 3.027 0 000-.74l4.94-2.47C13.456 7.68 14.19 8 15 8z" />
              </svg>
              공유하기
            </button>
          </div>

          {/* 미리보기 */}
          <div className="mt-4">
            <h3 className="text-lg font-medium mb-2 dark:text-gray-200">노트 미리보기:</h3>
            <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-md overflow-auto max-h-[300px] text-sm border dark:border-gray-700">
              <pre className="whitespace-pre-wrap font-mono dark:text-gray-300">{result.markdownContent}</pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}