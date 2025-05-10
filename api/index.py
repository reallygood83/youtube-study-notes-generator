from http.server import BaseHTTPRequestHandler
import json
import os
import re
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi, _errors as yt_errors

# 환경 변수에서 API 키 가져오기
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# 디버깅을 위한 로그 함수
def log_message(message):
    with open("/tmp/api_log.txt", "a") as f:
        f.write(f"{message}\n")

# 간단한 학습 노트 생성 함수 (테스트용)
def generate_simple_note(text):
    return f"""
# 학습 노트

## 학습 목표
- 이 자료를 통해 주요 개념을 이해하기

## 핵심 개념
- 텍스트에서 추출한 핵심 개념

## 요약
{text[:500]}...

## 응용
- 이 지식을 실제로 활용하는 방법

## 자체 평가
- 학습 내용을 잘 이해했는지 확인하는 질문
"""

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # 로그 기록
            log_message("POST 요청 받음")
            
            # 요청 데이터 읽기
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            # 로그 기록
            log_message(f"요청 데이터: {post_data}")
            
            request_data = json.loads(post_data)
            
            # 요청 데이터 검증
            if 'inputType' not in request_data or 'inputValue' not in request_data:
                self.send_error_response("유효하지 않은 요청입니다. inputType과 inputValue가 필요합니다.")
                return
            
            input_type = request_data['inputType']
            input_value = request_data['inputValue']
            
            # 로그 기록
            log_message(f"입력 타입: {input_type}, 입력 값 길이: {len(input_value)}")
            
            # 간단한 테스트 모드로 실행
            markdown_content = generate_simple_note(input_value)
            video_title = "테스트_노트"
            
            # 성공 응답
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            response_data = {
                "markdownContent": markdown_content,
                "videoTitle": video_title
            }
            
            response_json = json.dumps(response_data)
            log_message(f"응답 데이터 길이: {len(response_json)}")
            
            self.wfile.write(response_json.encode('utf-8'))
            
        except Exception as e:
            log_message(f"오류 발생: {str(e)}")
            self.send_error_response(str(e))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def send_error_response(self, error_message):
        self.send_response(400)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        response_data = {
            "error": error_message
        }
        
        log_message(f"오류 응답: {error_message}")
        self.wfile.write(json.dumps(response_data).encode('utf-8'))