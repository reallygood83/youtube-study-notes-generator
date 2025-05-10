from http.server import BaseHTTPRequestHandler
import json
import os
import sys
import traceback

# 디버깅을 위한 로그 함수
def log_message(message):
    with open("/tmp/api_debug.log", "a") as f:
        f.write(f"{message}\n")

# 간단한 학습 노트 생성 함수
def generate_simple_notes(text, learning_level='beginner'):
    try:
        # 텍스트가 너무 길면 잘라내기
        if len(text) > 1000:
            text = text[:1000] + "..."
        
        # 레벨에 따른 간단한 노트 생성
        level_prefix = "고급 " if learning_level == 'advanced' else "기본 "
        
        markdown_content = f"""
# {level_prefix}학습 노트

## 학습 목표
- 이 자료의 주요 개념 이해하기
- 핵심 아이디어 파악하기

## 핵심 개념
- 주요 개념 1
- 주요 개념 2
- 주요 개념 3

## 요약
{text[:200]}...

## 응용
- 이 지식을 실제로 활용하는 방법

## 자체 평가
- 학습 내용을 잘 이해했나요?
- 핵심 개념을 설명할 수 있나요?
"""
        return markdown_content
    except Exception as e:
        log_message(f"노트 생성 오류: {str(e)}")
        log_message(traceback.format_exc())
        return "노트 생성 중 오류가 발생했습니다."

# HTTP 요청 핸들러
class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            log_message("POST 요청 받음")
            
            # 요청 데이터 읽기
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            log_message(f"요청 데이터: {post_data}")
            
            data = json.loads(post_data)
            input_type = data.get('inputType', 'text')
            input_value = data.get('inputValue', '')
            learning_level = data.get('learningLevel', 'beginner')
            
            log_message(f"입력 타입: {input_type}, 학습 레벨: {learning_level}")
            log_message(f"입력 값 길이: {len(input_value)}")
            
            # 간단한 노트 생성
            markdown_content = generate_simple_notes(input_value, learning_level)
            
            # 응답 준비
            response_data = {
                'markdownContent': markdown_content,
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
            log_message("응답 성공")
            
        except Exception as e:
            log_message(f"오류 발생: {str(e)}")
            log_message(traceback.format_exc())
            
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
        log_message("OPTIONS 요청 받음")
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers() 