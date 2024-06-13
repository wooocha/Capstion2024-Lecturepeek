from django.db import transaction

from .script import get_script
from .get_note_prompt import generate_lecture_notes
from .get_paragraph_prompt import generate_script
from .stt import speech_to_text
from .script import script_to_json
from .script import get_video_id
from .translate import translate_json
from Lecturepeek.models import Video, SummaryNote, Script, Test
import json
import time
import os
import random


def make_note(video_url, option):
    current_dir = os.getcwd()
    service_dir = os.path.join(os.path.join(current_dir, "Lecturepeek"), "service")
    log_dir = os.path.join(service_dir, "log")
    script_json = ""
    video_id = get_video_id(video_url)
    lecture_note = ""
    start_time = time.time()

    loaded_data = load_data(video_id, option)
    # db 에 video_id 검색 후 결과가 있으면 바로 반환
    if loaded_data:
        return loaded_data
    # db 에 결과가 없으면 추출 시작.
    else:
        if option == '1':
            processed_script, pure_script = get_script(video_url)
            if processed_script:
                # 자막이 있는 경우 강의 노트를 생성합니다.
                print("자막 기반 강의노트 생성")
                lecture_script = generate_script(processed_script)
                script_json = script_to_json(lecture_script)
                lecture_note = generate_lecture_notes(lecture_script)
                # 결과를 출력합니다.
            else:
                print("해당 영상에 자막을 찾을 수 없습니다..")  # 자막을 가져오지 못한 경우 메시지를 출력합니다.
                return 'err'
        elif option == '2':
            print("음성 기반 강의노트 생성")
            lecture_script = speech_to_text(video_url)
            script_json = script_to_json(lecture_script)
            lecture_note = generate_lecture_notes(lecture_script)
        else:
            print("옵션 에러")

        end_time = time.time()
        time_elapsed = end_time - start_time
        lt = time.localtime(start_time)
        today = time.strftime("%m-%d-%H-%M-%S", lt)
        filename = f"{video_id}lecturenote{today}.txt"

        file_path = os.path.join(log_dir, filename)

        translated_lecture_note = translate_json(lecture_note)
        data1 = json.loads(translated_lecture_note)
        data2 = json.loads(script_json)
        merged_data = {**data1, **data2}
        merged_json_str = json.dumps(merged_data, indent=2, ensure_ascii=False)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"소요시간 : {time_elapsed} \n")
            f.write(f"영상링크 : {video_url}\n")
            f.write(f"추출방식 : {option}\n")
            f.write(merged_json_str)

        save_data(merged_json_str, option, video_id)
        return merged_json_str


def load_data(vid, option):
    existing_video = Video.objects.filter(video_id=vid, creation_type=option).first()
    if existing_video:
        # 기존 비디오와 연결된 모든 데이터를 JSON으로 반환
        summary_notes = SummaryNote.objects.filter(video=existing_video)
        scripts = Script.objects.filter(video=existing_video)
        questions = Test.objects.filter(video=existing_video)

        summary_notes_data = [{
            'timestamp': note.timestamp,
            'section_title': note.section_title,
            'content': note.content
        } for note in summary_notes]

        scripts_data = [{
            'timestamp': script.timestamp,
            'content': script.content
        } for script in scripts]

        questions_data = [{
            'question': question.question,
            'answer': question.answer
        } for question in questions]

        response_data = {
            'videoTitle': existing_video.title,
            'videoDescription': existing_video.description,
            'Lecture Note': summary_notes_data,
            'script': scripts_data,
            'questions': questions_data
        }
        return json.dumps(response_data)
    else:
        return None


def save_data(data, option, vid):
    try:
        data = json.loads(data)
        with transaction.atomic():
            # 비디오 객체 생성
            video = Video.objects.create(
                video_id=vid,
                creation_type=option,
                title=data['videoTitle'],
                description=data['videoDescription']
            )

            # 요약 노트 객체 생성
            for note in data['Lecture Note']:
                SummaryNote.objects.create(
                    video=video,
                    timestamp=note['timestamp'],
                    section_title=note['section_title'],
                    content=note['content']
                )

            # 스크립트 객체 생성
            for script in data['script']:
                Script.objects.create(
                    video=video,
                    timestamp=script['timestamp'],
                    content=script['content']
                )

            # 문제 객체 생성
            for question in data['questions']:
                Test.objects.create(
                    video=video,
                    question=question['question'],
                    answer=question['answer']
                )
    except Exception as e:
        print(e)
        return e


def load_rand_data():
    count = Video.objects.count()
    random_index = random.randint(0, count - 1)
    existing_video = Video.objects.all()[random_index]
    print("랜덤")
    if existing_video:
        # 기존 비디오와 연결된 모든 데이터를 JSON으로 반환
        summary_notes = SummaryNote.objects.filter(video=existing_video)
        scripts = Script.objects.filter(video=existing_video)
        questions = Test.objects.filter(video=existing_video)

        summary_notes_data = [{
            'timestamp': note.timestamp,
            'section_title': note.section_title,
            'content': note.content
        } for note in summary_notes]

        scripts_data = [{
            'timestamp': script.timestamp,
            'content': script.content
        } for script in scripts]

        questions_data = [{
            'question': question.question,
            'answer': question.answer
        } for question in questions]

        response_data = {
            'videoTitle': existing_video.title,
            'videoDescription': existing_video.description,
            'Lecture Note': summary_notes_data,
            'script': scripts_data,
            'questions': questions_data
        }
        return json.dumps(response_data)
    else:
        return None