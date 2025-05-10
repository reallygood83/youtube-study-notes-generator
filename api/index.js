// Next.js API 라우트 핸들러
import { exec } from 'child_process';
import { createServer } from 'http';
import { parse } from 'url';

// FastAPI 앱으로 요청을 프록시하는 함수
export default async function handler(req, res) {
  try {
    // 요청 모든 경로를 FastAPI 앱으로 전달
    const { method, body, headers } = req;
    
    // FastAPI 엔드포인트로의
    const url = 'http://localhost:8000' + req.url;
    
    // FastAPI 서버 시작 (이미 실행 중이면 무시됨)
    startFastAPIServer();
    
    // 3초 대기 (FastAPI 서버가 시작될 시간)
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // 실제 요청 수행
    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
        ...headers
      },
      body: method !== 'GET' && method !== 'HEAD' ? JSON.stringify(body) : undefined,
    });
    
    // FastAPI 응답 헤더 설정
    Object.entries(response.headers).forEach(([key, value]) => {
      res.setHeader(key, value);
    });
    
    // 응답 전달
    const data = await response.json();
    res.status(response.status).json(data);
  } catch (error) {
    console.error('API 프록시 오류:', error);
    res.status(500).json({
      error: '서버 오류가 발생했습니다',
      details: error.message
    });
  }
}

// FastAPI 서버 시작 함수
let fastAPIServerRunning = false;
function startFastAPIServer() {
  if (fastAPIServerRunning) return;
  
  try {
    const process = exec('cd api && uvicorn fastapi_app:app --reload --port 8000', 
      (error, stdout, stderr) => {
        if (error) {
          console.error(`FastAPI 서버 시작 오류: ${error.message}`);
          return;
        }
        console.log('FastAPI 서버 로그:', stdout);
        if (stderr) console.error('FastAPI 서버 오류:', stderr);
      }
    );
    
    process.on('exit', (code) => {
      console.log(`FastAPI 서버 종료됨, 코드: ${code}`);
      fastAPIServerRunning = false;
    });
    
    fastAPIServerRunning = true;
    console.log('FastAPI 서버 시작됨');
  } catch (error) {
    console.error('FastAPI 서버 시작 실패:', error);
  }
} 