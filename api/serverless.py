from flask import Flask, request, jsonify
import json
import os
import re
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi, _errors as yt_errors
import requests

# 환경 변수에서 API 키 가져오기 (먼저 .env 파일에서 로드 시도)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv 모듈이 없는 경우 무시

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# API 키 상태 로깅
if GEMINI_API_KEY:
    print("Gemini API 키가 정상적으로 로드되었습니다.")
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("경고: Gemini API 키가 환경 변수에 설정되어 있지 않습니다.")

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
    # 입력 길이 확인 및 로깅
    original_length = len(transcript_text)
    max_length = 25000  # 안전한 토큰 한도를 위해 더 줄임

    # 자막 길이가 제한을 초과할 경우
    if original_length > max_length:
        print(f"경고: 자막이 너무 깁니다 ({original_length}자). {max_length}자로 잘라냅니다.")
        transcript_text = transcript_text[:max_length]
        transcript_text += f"\n\n[참고: 원본 자막이 너무 길어 {max_length}자로 잘랐습니다. 전체 내용의 약 {int(max_length/original_length*100)}%만 처리되었습니다.]"

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
        level_context = """
고급 학습자를 위한 자료를 만들어 주세요:
- 더 심층적인 분석과 고급 개념 설명을 포함하세요
- 학술적 용어와 전문 개념을 적절히 사용하세요
- 비판적 사고를 요하는 더 복잡한 자기 평가 질문을 포함하세요
"""
    else:
        level_context = """
초보 학습자를 위한 자료를 만들어 주세요:
- 기본 개념을 쉽게 이해할 수 있는 설명을 제공하세요
- 복잡한 용어는 간단한 설명과 예시를 함께 제공하세요
- 일상생활에서 적용할 수 있는 실용적인 예시를 포함하세요
"""

    prompt = f"""아래 유튜브 영상 스크립트를 바탕으로 학습 노트를 만들어주세요.
{video_context}
{level_context}

학습 노트는 다음 구조로 작성해 주세요 (모든 섹션은 마크다운 형식으로 작성):
1. 학습 목표 - 이 노트를 통해 배울 수 있는 주요 내용 (3-5개 항목)
2. 핵심 개념 - 중요 키워드와 그에 대한 간결한 설명
3. 개념 지도 - 주요 개념 간의 관계를 보여주는 구조 (마크다운으로 표현)
4. 자세한 내용 분석 - 주제별 체계적인 설명
5. 요약 - 핵심 내용의 간략한 정리
6. 응용 방법 - 학습 내용을 실생활이나 실무에 적용하는 방법
7. 자체 평가 질문 - 이해도를 확인할 수 있는 질문 (3-5개)

스크립트:
{transcript_text}
"""

    # API 키 검증
    if not GEMINI_API_KEY:
        print("오류: Gemini API 키가 없습니다. 환경 변수를 확인하세요.")
        error_message = """
# API 키 오류

API 키가 설정되어 있지 않아 학습 노트를 생성할 수 없습니다.

## 해결 방법
1. 환경 변수에 `GEMINI_API_KEY`를 설정하세요
2. Vercel 프로젝트 설정에서 환경 변수를 확인하세요
3. 개발 환경에서는 `.env` 또는 `.env.local` 파일을 통해 API 키를 설정할 수 있습니다

## 지원
문제가 지속되면 개발자에게 문의하세요.
"""
        return error_message

    # API 호출 시도
    try:
        print("Gemini API 호출 시작")
        try:
            print("gemini-pro 모델 사용 시도")
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            print("gemini-pro 모델 호출 성공")
            return response.text
        except Exception as e:
            print(f"gemini-pro 모델 오류: {str(e)}, gemini-1.5-flash 모델로 대체")
            try:
                # Pro 모델이 실패하면 1.5 모델로 시도
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                print("gemini-1.5-flash 모델 호출 성공")
                return response.text
            except Exception as e2:
                print(f"gemini-1.5-flash 모델 오류: {str(e2)}")
                # 두 모델 모두 실패하면 PaLM 모델로 시도
                try:
                    model = genai.GenerativeModel('text-bison')
                    response = model.generate_content(prompt)
                    print("PaLM text-bison 모델 호출 성공")
                    return response.text
                except Exception as e3:
                    print(f"모든 모델 호출 실패: {str(e3)}")
                    raise Exception("모든 AI 모델 호출에 실패했습니다. 잠시 후 다시 시도해 주세요.")
    except Exception as e:
        print(f"노트 생성 중 오류: {str(e)}")
        error_detail = str(e)

        # 일반적인 오류 메시지 대신 구체적인 오류 안내 제공
        if "quota" in error_detail.lower():
            raise Exception("API 할당량 초과: 현재 너무 많은 요청이 있습니다. 잠시 후 다시 시도해 주세요.")
        elif "timeout" in error_detail.lower():
            raise Exception("API 타임아웃: 서버 응답이 너무 오래 걸립니다. 더 짧은 영상으로 시도해 보세요.")
        elif "content" in error_detail.lower() and "blocked" in error_detail.lower():
            raise Exception("콘텐츠 정책 제한: 입력된 콘텐츠에 제한된 내용이 포함되어 있을 수 있습니다.")
        else:
            raise Exception(f"학습 노트 생성 중 오류가 발생했습니다: {error_detail}")

@app.route('/api', methods=['POST', 'OPTIONS'])
def generate_notes():
    # CORS 헤더 설정
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    }

    # OPTIONS 요청 처리 (CORS 프리플라이트)
    if request.method == 'OPTIONS':
        return '', 200, headers

    try:
        print("API 요청 시작")
        # 요청 데이터 받기
        data = request.get_json()
        if not data:
            print("요청 데이터 없음")
            return jsonify({
                'error': '요청 데이터를 읽을 수 없습니다. Content-Type이 application/json인지 확인하세요.'
            }), 400, headers

        print(f"받은 요청 데이터: {data}")

        # 요청 데이터 검증
        if 'inputType' not in data or 'inputValue' not in data:
            print("필수 필드 누락")
            return jsonify({
                'error': '유효하지 않은 요청입니다. inputType과 inputValue가 필요합니다.',
                'receivedData': data
            }), 400, headers

        input_type = data['inputType']
        input_value = data['inputValue']
        learning_level = data.get('learningLevel', 'beginner')

        # 빈 입력값 검증
        if not input_value or len(input_value.strip()) == 0:
            print("빈 입력값 오류")
            return jsonify({
                'error': '입력값이 비어 있습니다. 유튜브 URL 또는 스크립트 내용을 입력해주세요.'
            }), 400, headers

        print(f"입력 타입: {input_type}, 학습 레벨: {learning_level}, 입력값 길이: {len(input_value)}")

        # 입력 타입에 따라 처리
        transcript_text = ""
        video_title = "유튜브_학습"
        video_info = None

        if input_type == 'url':
            # URL에서 비디오 ID 추출
            video_id = extract_video_id(input_value)
            if not video_id:
                print(f"잘못된 URL 형식: {input_value}")
                return jsonify({
                    'error': '유효한 유튜브 URL이 아닙니다. 올바른 유튜브 영상 URL을 입력해주세요.',
                    'helpText': '예시: https://www.youtube.com/watch?v=abcdefg1234'
                }), 400, headers

            print(f"비디오 ID 추출 성공: {video_id}")

            # 비디오 정보 가져오기
            try:
                video_info = get_video_info(video_id)
                video_title = video_info.get('title', f"Video_{video_id}")
                print(f"비디오 정보 가져오기 성공: {video_title}")
            except Exception as e:
                print(f"비디오 정보 가져오기 실패: {str(e)}")
                # 정보 가져오기 실패해도 계속 진행

            try:
                # 유튜브 자막 가져오기 시도
                transcript_text = get_youtube_transcript(video_id)
                print(f"자막 가져오기 성공: {len(transcript_text)}자")
            except Exception as e:
                error_msg = str(e)
                print(f"자막 가져오기 실패: {error_msg}")

                # 특정 오류에 대한 사용자 친화적 메시지 제공
                if "TranscriptsDisabled" in error_msg or "자막이 비활성화" in error_msg:
                    return jsonify({
                        'error': '이 영상의 자막이 비활성화되어 있습니다.',
                        'recommendationText': '해결 방법: 1) 다른 영상을 시도하거나, 2) 텍스트 직접 입력 모드를 이용해 스크립트를 수동으로 입력하세요.',
                        'errorType': 'TRANSCRIPTS_DISABLED'
                    }), 400, headers
                elif "NoTranscriptAvailable" in error_msg or "자막이 제공되지 않는" in error_msg:
                    return jsonify({
                        'error': '이 영상에 자막이 제공되지 않습니다.',
                        'recommendationText': '해결 방법: 1) 자막이 있는 다른 영상을 시도하거나, 2) 텍스트 직접 입력 모드를 이용해 스크립트를 수동으로 입력하세요.',
                        'errorType': 'NO_TRANSCRIPT'
                    }), 400, headers
                elif "VideoUnavailable" in error_msg or "접근할 수 없는" in error_msg:
                    return jsonify({
                        'error': '영상을 찾을 수 없거나 접근이 제한되어 있습니다.',
                        'recommendationText': '해결 방법: 1) URL이 올바른지 확인하고, 2) 해당 영상이 비공개이거나 삭제되지 않았는지 확인하세요.',
                        'errorType': 'VIDEO_UNAVAILABLE'
                    }), 400, headers
                else:
                    return jsonify({
                        'error': f'자막을 가져오는 중 오류가 발생했습니다: {error_msg}',
                        'recommendationText': '다른 영상을 시도하거나 텍스트 직접 입력 모드를 이용해보세요.',
                        'errorType': 'TRANSCRIPT_ERROR'
                    }), 400, headers
        else:  # input_type == 'text'
            # 사용자가 직접 입력한 스크립트 사용
            transcript_text = input_value
            print("직접 입력 텍스트 모드")

        # 학습 노트 생성 전 텍스트 검증
        if len(transcript_text.strip()) < 50:
            print(f"텍스트가 너무 짧음: {len(transcript_text)}자")
            return jsonify({
                'error': '입력된 텍스트가 너무 짧습니다. 학습 노트를 생성하기 위해서는 더 많은 내용이 필요합니다.',
                'recommendationText': '최소 50자 이상의 텍스트를 입력해주세요.'
            }), 400, headers

        print("학습 노트 생성 시작")
        # 학습 노트 생성
        markdown_content = generate_notes_with_gemini(transcript_text, video_info, learning_level)
        print(f"학습 노트 생성 완료: {len(markdown_content)}자")

        # 성공 응답
        response_data = {
            "markdownContent": markdown_content,
            "videoTitle": video_title,
            "processingInfo": {
                "textLength": len(transcript_text),
                "modelUsed": "gemini"
            }
        }

        print("API 요청 처리 완료")
        return jsonify(response_data), 200, headers

    except Exception as e:
        error_msg = str(e)
        print(f"API 요청 처리 중 오류: {error_msg}")

        # 오류 응답
        error_response = {
            'error': error_msg,
            'timestamp': str(import_timestamp())
        }

        # 429 오류 (할당량 초과) 처리
        if "quota" in error_msg.lower() or "rate" in error_msg.lower():
            error_response['errorType'] = 'QUOTA_EXCEEDED'
            error_response['recommendationText'] = '서버가 현재 많은 요청을 처리 중입니다. 잠시 후 다시 시도해주세요.'
            return jsonify(error_response), 429, headers

        return jsonify(error_response), 400, headers

# 타임스탬프 가져오기 함수
def import_timestamp():
    from datetime import datetime
    return datetime.now().isoformat()