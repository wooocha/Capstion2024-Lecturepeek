from youtube_transcript_api import YouTubeTranscriptApi
import re
import json


##### 유튜브 링크에서 자막 추출하기 #####
def get_video_id(url):
    # 유튜브 URL에서 비디오 ID를 추출하는 정규 표현식
    regex = re.compile(r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})')
    match = regex.search(url)
    return match.group(1) if match else None


def fetch_transcript(video_id):
    # 비디오 ID를 사용해 유튜브 자막을 가져오는 함수입니다.
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, ['en','en-US', 'hi', 'ko', 'es', 'ar','jp'])
        return transcript
    except Exception as e:
        # 자막을 가져오는 도중 오류가 발생하면 예외를 처리합니다.
        print(f"Error fetching transcript: {e}")
        return None


def preprocess_transcript(transcript):
    # 자막을 타임라인과 문장 형태로 전처리하는 함수입니다.
    timeline_script = []
    pure_script = []
    for entry in transcript:
        start_time = convert_to_mm_ss(entry['start'])
        text = entry['text']
        # 개행문자 공백으로 대체
        modified_text = text.replace("\n", " ")
        timeline_script.append(f"{start_time}: {modified_text}")
        pure_script.append(f"{modified_text}")

    return timeline_script, pure_script


def convert_to_mm_ss(time_value):
    # time_value를 문자열로 변환 후 second와 millisecond로 분리
    time_str = str(time_value)
    seconds, milliseconds = map(float, time_str.split('.'))

    # 총 시간을 초로 계산
    total_seconds = seconds + milliseconds / 1000

    # 분과 초로 변환
    minutes = int((total_seconds // 60) % 60)
    seconds = int(total_seconds % 60)
    hours = int(total_seconds // 3600)

    # mm:ss 형식으로 변환
    result = f"{hours:d}:{minutes:02d}:{seconds:02d}"
    return result


def get_script(video_url):
    video_id = get_video_id(video_url)  # 링크에서 비디오 ID를 추출합니다.
    pure_script = []

    if video_id:
        # 비디오 ID가 유효한 경우 자막을 가져옵니다.
        transcript = fetch_transcript(video_id)
        if transcript:
            # 자막을 성공적으로 가져온 경우 전처리합니다.
            processed_script, pure_script = preprocess_transcript(transcript)
            # script_text = "\n".join(processed_script)
    else:
        print("Invalid video URL")  # 비디오 ID가 유효하지 않은 경우 메시지를 출력합니다.
        return None

    return processed_script, pure_script


def script_to_json(lecture_script):
    # pattern = re.compile(r'(\d{1,2}:\d{2}:\d{2}): (.*?)(?=\d{1,2}:\d{2}:\d{2}:|$)', re.DOTALL)
    pattern = re.compile(r'(\d{1,2}:\d{2}:\d{2})\s*:\s*(.*?)(?=(\d{1,2}:\d{2}:\d{2}\s*:)|$)', re.DOTALL)
    matches = pattern.findall(lecture_script)

    script = []
    seen = set()

    for match in matches:
        timestamp, content, _ = match
        timestamp = timestamp.strip()
        content = content.strip()
        if timestamp and content:  # 빈 항목과 공백 항목을 제외
            script.append({"timestamp": timestamp, "content": content})

    # JSON 형식으로 출력
    json_output = {"script": script}
    json_str = json.dumps(json_output, indent=2, ensure_ascii=False)
    return json_str
