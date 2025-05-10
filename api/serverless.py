from flask import Flask, request, jsonify
import json
import os
import re
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi, _errors as yt_errors
import requests

# 환경 변수에서 API 키 가져오기
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Gemini API 설정
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Flask 앱 설정
app = Flask(__name__)

# 유튜브 비디오 ID 추출 함수
def extract_video_id(url):
    """유튜브 URL에서 비디오 ID를 추출합니다."""
    video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
    if video_id_match:
        return video_id_match.group(1)
    return None

# 유튜브 자막 가져오기 함수
def get_youtube_transcript(video_id):
    """유튜브 비디오 ID를 통해 자막을 가져옵니다."""
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko', 'en'])
        transcript_text = ' '.join([item['text'] for item in transcript_list])
        return transcript_text
    except yt_errors.NoTranscriptAvailable:
        raise Exception("이 영상에는 자막이 제공되지 않습니다. 스크립트 직접 입력 방식을 이용해주세요.")
    except yt_errors.TranscriptsDisabled:
        raise Exception("이 영상의 자막이 비활성화되어 있습니다. 스크립트 직접 입력 방식을 이용해주세요.")
    except yt_errors.VideoUnavailable:
        raise Exception("유효하지 않거나 접근할 수 없는 영상입니다.")
    except Exception as e:
        raise Exception(f"자막을 가져오는 중 오류가 발생했습니다: {str(e)}")

# 유튜브 비디오 정보 가져오기 함수
def get_video_info(video_id):
    """유튜브 비디오 ID로부터 제목과 설명을 가져옵니다."""
    try:
        url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            title = data.get('title', f"Video_{video_id}")
            return {
                'title': title,
                'video_id': video_id
            }
        else:
            return {
                'title': f"Video_{video_id}",
                'video_id': video_id
            }
    except Exception:
        return {
            'title': f"Video_{video_id}",
            'video_id': video_id
        }

# Gemini API를 사용하여 학습 노트 생성 함수
def generate_notes_with_gemini(transcript_text, video_info=None, learning_level='beginner'):
    """Gemini API를 사용하여 주어진 자막으로 학습 노트를 생성합니다."""
    if len(transcript_text) > 30000:
        transcript_text = transcript_text[:30000]
    
    # 비디오 정보가 있으면 프롬프트에 추가
    video_context = ""
    if video_info:
        video_context = f"""
이 학습 노트는 다음 유튜브 영상을 기반으로 합니다:
제목: {video_info.get('title', '알 수 없는 제목')}
비디오 ID: {video_info.get('video_id', '알 수 없는 ID')}
"""
    
    # 학습 레벨 설정
    level_context = ""
    if learning_level == 'advanced':
        level_context = "고급 학습자를 위한 자료를 만들어 주세요."
    else:
        level_context = "초보 학습자를 위한 자료를 만들어 주세요."
    
    prompt = f"""아래 유튜브 영상 스크립트를 바탕으로 학습 노트를 만들어주세요.
{video_context}
{level_context}

학습 노트에는 다음 요소가 포함되어야 합니다:
1. 학습 목표
2. 핵심 개념 (키워드와 설명)
3. 개념 지도 (개념 간의 연결을 보여주는 구조)
4. 자세한 내용 분석
5. 요약
6. 응용 방법
7. 자체 평가 질문

스크립트:
{transcript_text}
"""

    if not GEMINI_API_KEY:
        raise Exception("GEMINI_API_KEY가 설정되어 있지 않습니다.")

    try:
        if GEMINI_API_KEY:
            try:
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content(prompt)
                return response.text
            except Exception:
                # Pro 모델이 실패하면 1.5 모델로 시도
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                return response.text
        else:
            return "API 키가 설정되어 있지 않습니다."
    except Exception as e:
        raise Exception(f"학습 노트 생성 중 오류가 발생했습니다: {str(e)}")

@app.route('/api', methods=['POST', 'OPTIONS'])
def generate_notes():
    # CORS 헤더 설정
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }
    
    # OPTIONS 요청 처리 (CORS 프리플라이트)
    if request.method == 'OPTIONS':
        return '', 200, headers
    
    try:
        # 요청 데이터 받기
        data = request.get_json()
        
        # 요청 데이터 검증
        if not data or 'inputType' not in data or 'inputValue' not in data:
            return jsonify({'error': '유효하지 않은 요청입니다. inputType과 inputValue가 필요합니다.'}), 400, headers
        
        input_type = data['inputType']
        input_value = data['inputValue']
        learning_level = data.get('learningLevel', 'beginner')
        
        # 입력 타입에 따라 처리
        transcript_text = ""
        video_title = "유튜브_학습"
        video_info = None
        
        if input_type == 'url':
            # URL에서 비디오 ID 추출
            video_id = extract_video_id(input_value)
            if not video_id:
                return jsonify({'error': '유효한 유튜브 URL이 아닙니다.'}), 400, headers
            
            # 비디오 정보 가져오기
            video_info = get_video_info(video_id)
            video_title = video_info.get('title', f"Video_{video_id}")
            
            try:
                # 유튜브 자막 가져오기 시도
                transcript_text = get_youtube_transcript(video_id)
            except Exception as e:
                # 자막 가져오기 실패 시 사용자 친화적 오류 메시지
                return jsonify({'error': str(e)}), 400, headers
        else:  # input_type == 'text'
            # 사용자가 직접 입력한 스크립트 사용
            transcript_text = input_value
        
        # 학습 노트 생성
        markdown_content = generate_notes_with_gemini(transcript_text, video_info, learning_level)
        
        # 성공 응답
        response_data = {
            "markdownContent": markdown_content,
            "videoTitle": video_title
        }
        
        return jsonify(response_data), 200, headers
        
    except Exception as e:
        # 오류 응답
        return jsonify({'error': str(e)}), 400, headers