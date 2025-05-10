# API 서버

이 디렉토리는 유튜브 스터디 노트 제너레이터의 서버리스 API 구현을 포함합니다.

## 주요 파일

- `serverless.py`: Vercel 서버리스 환경에서 실행되는 메인 API 구현
- `index.py`: 원래 API 구현(이전 버전)
- `api.py`: API 엔드포인트 정의
- `vercelHandler.py`: Vercel 서버리스 함수 핸들러

## API 엔드포인트

- `/api`: POST 요청을 통해 노트 생성 요청을 처리합니다.

## 입력 파라미터

- `inputType`: 'url' 또는 'text'
- `inputValue`: 유튜브 URL 또는 직접 입력된 스크립트 텍스트
- `learningLevel`: 'beginner' 또는 'advanced' (기본값: 'beginner')

## 주의사항

- 환경 변수 `GEMINI_API_KEY`가 설정되어 있어야 합니다.
- 유튜브 URL을 사용할 경우 자막이 활성화된 영상만 처리할 수 있습니다.
- 입력 텍스트 길이는 최대 25,000자로 제한됩니다.
EOL < /dev/null