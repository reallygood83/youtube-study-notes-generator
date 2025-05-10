from http.server import BaseHTTPRequestHandler
import importlib.util
import sys
import os
import json

# fastapi_app.py 모듈 경로 설정
module_path = os.path.join(os.path.dirname(__file__), 'fastapi_app.py')

# 모듈 스펙 로드
spec = importlib.util.spec_from_file_location('fastapi_app', module_path)
fastapi_app = importlib.util.module_from_spec(spec)
sys.modules['fastapi_app'] = fastapi_app
spec.loader.exec_module(fastapi_app)

# HTTP 요청 핸들러
class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # 요청 데이터 읽기
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(post_data)
            
            # FastAPI 앱의 generate_notes 함수 호출
            result = fastapi_app.generate_notes_with_gemini(
                transcript_text=data.get('inputValue', ''),
                learning_level=data.get('learningLevel', 'beginner')
            )
            
            # 응답 준비
            response_data = {
                'markdownContent': result,
                'videoTitle': "YouTube 학습 노트"
            }
            
            # 성공 응답
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            response = json.dumps(response_data)
            self.wfile.write(response.encode('utf-8'))
            
        except Exception as e:
            # 오류 응답
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            error_response = json.dumps({
                'error': str(e),
                'errorType': 'SERVER_ERROR'
            })
            self.wfile.write(error_response.encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers() 