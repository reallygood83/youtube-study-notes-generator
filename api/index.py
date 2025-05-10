from http.server import BaseHTTPRequestHandler
import json
import os
import re
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi, _errors as yt_errors

# 환경 변수에서 API 키 가져오기
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Gemini API 설정
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# 유튜브 비디오 ID 추출 함수
def extract_video_id(url):
    """유튜브 URL에서 비디오 ID를 추출합니다."""
    video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
    if video_id_match:
        return video_id_match.group(1)
    return None

# 유튜브 비디오 제목 가져오기 함수
def get_video_title(video_id):
    """유튜브 비디오 ID로부터 제목을 가져옵니다."""
    return f"Video_{video_id}"

# 유튜브 자막 가져오기 함수
def get_youtube_transcript(video_id):
    """유튜브 비디오 ID를 통해 자막을 가져옵니다."""
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko', 'en'])
        transcript_text = ' '.join([item['text'] for item in transcript_list])
        return transcript_text
    except yt_errors.NoTranscriptAvailable:
        raise Exception("이 영상에는 자막이 제공되지 않습니다.")
    except yt_errors.TranscriptsDisabled:
        raise Exception("이 영상의 자막이 비활성화되어 있습니다.")
    except yt_errors.VideoUnavailable:
        raise Exception("유효하지 않거나 접근할 수 없는 영상입니다.")
    except Exception as e:
        raise Exception(f"자막을 가져오는 중 오류가 발생했습니다: {str(e)}")

# Gemini API를 사용하여 학습 노트 생성 함수
def generate_notes_with_gemini(transcript_text):
    """Gemini API를 사용하여 주어진 자막으로 학습 노트를 생성합니다."""
    prompt = """# 유튜브 대본 티칭 머신

## 역할: 적응형 교육 합성기  
귀하는 YouTube 원본 스크립트를 최적화된 학습 자료로 변환하는 전문 교육 콘텐츠 처리 전문가입니다. 고급 교육 프레임워크를 활용합니다.

## 역량  
1.  **콘텐츠 분석 및 추출**  
    - 필사본에서 핵심 개념, 사실, 이론 및 방법론 추출  
    - 개념적 계층과 지식 구조를 식별합니다.  
    - 강사의 교육 접근 방식과 방법을 인식합니다.  
    - 관련 없는 내용, 불필요한 단어, 반복을 걸러냅니다.  
    - 검증을 위해 잠재적인 부정확성이나 뒷받침되지 않는 주장을 표시합니다.  
2.  **교육 구조 조정**  
    - 교육 모범 사례에 따라 콘텐츠를 구성합니다.  
    - 콘텐츠에 기반한 명확한 학습 목표 개발  
    - 논리적인 지식 진행(기초 → 고급)을 생성합니다.  
    - 잠재적인 혼란 지점을 식별하고 명확히 합니다.  
    - 복잡한 주제를 관리 가능한 학습 단위로 나누세요  
3.  **학습 스타일 적응**  
    - 다양한 인지적 접근 방식(분석적, 실용적, 창의적)에 적응  
    - 다양한 지능 유형(논리, 언어, 공간 등)에 맞춰 조정 가능  
    - 다양한 주의 지속 시간과 처리 속도에 맞게 조정  
    - 도전적인 개념에 대한 대체 설명 제공

## 프로세스  
1.  **입력 분석**  
    - 주제, 범위, 복잡성 및 구조를 파악하기 위해 대본을 검토합니다.  
    - 교육 수준 및 선행 지식 확인  
    - 영상에서 사용된 원래의 교육 방식을 평가합니다.  
    - 원본 자료의 장점과 한계를 인식합니다.  
    - 필사본 품질을 평가하고 차이점이나 모호한 부분을 해결합니다.  
2.  **학습자 프로필 통합** (이 부분은 현재 MVP에서는 사용자 입력을 받지 않으므로, 일반적인 학습자 기준으로 처리해주세요.)  
    - 학습자의 특정 요구 사항, 목표 및 선호도를 고려합니다.  
    - 현재 지식 수준과 학습 맥락에 맞게 조정  
    - 학습 가능한 시간과 리소스를 최적화합니다.  
    - 언급된 경우 특정 학습 과제를 설명하십시오.  
    - 인지 부하 기능에 맞춰 콘텐츠 복잡성 조정  
3.  **콘텐츠 변환**  
    - 교육 자료를 일관된 교육 구조로 재구성합니다.  
    - 비유와 예를 통해 복잡한 개념을 단순화합니다.  
    - 불분명하거나 충분히 설명되지 않은 사항에 대해 자세히 설명하십시오.  
    - 새로운 정보를 기존 지식 프레임워크에 연결합니다.  
    - 사실의 정확성을 확인하고 추가 조사가 필요한 주장을 기록하세요.  
4.  **출력 생성**  
    - 가장 적합한 형식으로 기본 학습 자료를 만듭니다.  
    - 강화를 위한 보충 자료 개발  
    - 메타인지적 요소(반성 촉구, 자기 평가)를 포함합니다.  
    - 추가 탐색 및 적용을 위한 지침 제공  
5.  **품질 평가**  
    - 생성된 자료의 교육적 효과를 평가합니다.  
    - 남아 있는 격차나 불분명한 설명을 식별합니다.  
    - 표시된 부정확한 내용이 적절하게 처리되었는지 확인합니다.  
    - 모든 학습 목표가 적절하게 다루어졌는지 확인하세요.

## 필사본 품질 처리  
다양한 품질의 대본을 작업할 때:  
1.  **고품질 성적증명서**: 교육 최적화에 중점을 두고 표준 프로세스를 진행합니다.  
2.  **미완료 성적증명서의 경우**:  
    - 지식 격차를 파악하고 명확하게 기록합니다.  
    - 누락된 정보에 대한 보충 자료를 제안합니다.  
    - 사용 가능한 콘텐츠를 논리적으로 연결하여 일관성을 유지합니다.  
3.  **기술적/복잡한 사본의 경우**:  
    - 복잡한 용어를 추가 설명으로 분석합니다.  
    - 단순화된 비유와 시각적 표현을 사용하세요  
    - 기술 용어의 어휘집을 제공합니다.  
    - 학습자의 다양한 역량에 맞춰 점진적으로 복잡도를 높여줍니다.  
4.  **잠재적으로 부정확한 콘텐츠**:  
    - 의심스럽거나 근거가 없는 주장을 신고하세요.  
    - 진술이 확립된 지식과 충돌하는 경우 주의하세요  
    - 적절한 경우 검증 소스를 제안합니다.  
    - 확립된 사실과 화자의 의견을 구별합니다.

## 출력 구조 (이 구조에 맞춰 Markdown 형식으로 결과를 생성해주세요):  
1.  **학습 목표**  
    - 이 자료에서 배울 내용  
2.  **핵심 개념**  
    - 명확한 설명과 함께 제시된 필수 아이디어  
3.  **개념 지도**  
    - 아이디어가 연결되는 방식을 보여주는 ASCII 시각적 표현 (Markdown 코드 블록으로 표현 가능)  
4.  **자세한 분석**  
    - 콘텐츠에 대한 체계적인 설명  
5.  **요약**  
    - 가장 중요한 요점에 대한 간략한 검토  
6.  **응용**  
    - 이 지식을 실제로 사용하는 방법  
7.  **자체 평가**  
    - 이해도를 확인하기 위한 질문

---
{transcript_text}
---

위 스크립트(또는 스크립트 부재 정보)를 바탕으로, 앞서 정의된 "## 역할", "## 역량", "## 프로세스", "## 필사본 품질 처리"를 고려하여 "## 출력 구조"에 따라 교육적인 학습 노트를 Markdown 형식으로 작성해주십시오.""".format(transcript_text=transcript_text)

    if not GEMINI_API_KEY:
        raise Exception("GEMINI_API_KEY가 설정되어 있지 않습니다. 환경 변수를 확인하세요.")

    try:
        # Gemini 2.0 Flash 모델 사용 (사용자 요청에 따라)
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        raise Exception(f"AI 모델 호출 중 오류가 발생했습니다: {str(e)}")

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            request_data = json.loads(post_data)
            
            # 요청 데이터 검증
            if 'inputType' not in request_data or 'inputValue' not in request_data:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "유효하지 않은 요청입니다."}).encode('utf-8'))
                return
            
            input_type = request_data['inputType']
            input_value = request_data['inputValue']
            
            # 입력 타입에 따라 처리
            transcript_text = ""
            video_title = "유튜브_학습"
            
            if input_type == 'url':
                # URL에서 비디오 ID 추출
                video_id = extract_video_id(input_value)
                if not video_id:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "유효한 유튜브 URL이 아닙니다."}).encode('utf-8'))
                    return
                
                # 비디오 제목 가져오기
                video_title = get_video_title(video_id)
                
                # 유튜브 자막 가져오기
                transcript_text = get_youtube_transcript(video_id)
            else:  # input_type == 'text'
                # 사용자가 직접 입력한 스크립트 사용
                transcript_text = input_value
            
            # 학습 노트 생성
            markdown_content = generate_notes_with_gemini(transcript_text)
            
            # 성공 응답
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response_data = {
                "markdownContent": markdown_content,
                "videoTitle": video_title
            }
            
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
            
        except Exception as e:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()