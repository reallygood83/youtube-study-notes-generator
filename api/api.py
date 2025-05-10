from flask import request, jsonify
from index import app, log_message, extract_video_id, get_video_info, get_youtube_transcript, generate_notes_with_gemini

@app.route('/api', methods=['POST', 'OPTIONS'])
def api_endpoint():
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
        # 로그 기록
        log_message("POST 요청 받음")
        
        # 요청 데이터 받기
        data = request.get_json()
        
        # 로그 기록
        log_message(f"요청 데이터: {data}")
        
        # 요청 데이터 검증
        if not data or 'inputType' not in data or 'inputValue' not in data:
            log_message("유효하지 않은 요청 데이터")
            return jsonify({'error': '유효하지 않은 요청입니다. inputType과 inputValue가 필요합니다.'}), 400, headers
        
        input_type = data['inputType']
        input_value = data['inputValue']
        learning_level = data.get('learningLevel', 'beginner')
        
        # 로그 기록
        log_message(f"입력 타입: {input_type}, 입력 값 길이: {len(input_value)}, 학습 레벨: {learning_level}")
        
        # 입력 타입에 따라 처리
        transcript_text = ""
        video_title = "유튜브_학습"
        video_info = None
        
        if input_type == 'url':
            # URL에서 비디오 ID 추출
            video_id = extract_video_id(input_value)
            if not video_id:
                log_message("유효하지 않은 유튜브 URL")
                return jsonify({'error': '유효한 유튜브 URL이 아닙니다.'}), 400, headers
            
            # 비디오 정보 가져오기
            video_info = get_video_info(video_id)
            video_title = video_info.get('title', f"Video_{video_id}")
            
            try:
                # 유튜브 자막 가져오기 시도
                transcript_text = get_youtube_transcript(video_id)
            except Exception as e:
                # 자막 가져오기 실패 시 사용자 친화적 오류 메시지
                log_message(f"자막 가져오기 오류: {str(e)}")
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
        
        log_message("응답 데이터 생성 완료")
        return jsonify(response_data), 200, headers
        
    except Exception as e:
        # 오류 로그
        log_message(f"오류 발생: {str(e)}")
        
        # 오류 응답
        return jsonify({'error': str(e)}), 400, headers