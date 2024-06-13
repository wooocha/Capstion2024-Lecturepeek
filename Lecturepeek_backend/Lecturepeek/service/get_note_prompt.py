import json

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import (
    ChatPromptTemplate,
)
from langchain_core.output_parsers import StrOutputParser
import tiktoken

load_dotenv()
params = {
    "temperature": 0.4,  # 생성된 텍스트의 다양성 조정
    "max_tokens": 10000,  # 생성할 최대 토큰 수
}
model = ChatOpenAI(model="gpt-3.5-turbo-16k", **params)

# LangChain template 을 사용해 LLM 에게 작성할 프롬프트 템플릿을 정의합니다.
system_template = """
You're a meticulous lecture note-maker. When you get a subtitles for a lecture video, write a lecture note based on it. You must follow these steps:

1. **Summarize and Explain**: Summarize the main points and provide comprehensive explanations, presenting them under appropriate headings.
2. **Clear and Cohesive Notes**: Ensure the lecture note is clear, cohesive, and formatted into paragraphs under each heading.
3. **Include Timestamps**: Include the timestamp information at the start of each section.
4. **Use Emojis**: Use various emojis to symbolize different sections.
5. **Omit Unnecessary Content**: Delete any contents about subscribing to the channel and liking the video.
6. **Terminology definition**: If a terminology comes up, it provides a simple definition to help you understand.
7. **Create Questions**: Make three short-answer questions about the lecture. The answer must be 1~2 words.
8. **JSON Format**: Finally, present the lecture note in JSON format. The JSON should have the following structure:

Example JSON format: 
\"\"\"
{format}
\"\"\"
"""

json_format = """
{
    "videoTitle": "[video title]",
    "videoDescription": "[one-line video description]"
    "Lecture Note": [
    { "timestamp": "00:00:00",
    "section_title": "[appropriate emoji][section title]",
    "content": "[section contents]" },
    ... more Lecture Notes
    ],
    "questions":[
    {"question" : "[question text]",
    "answer":"[answer]"},
    {"question" : "[question text]",
    "answer":"[answer]"},
    {"question" : "[question text]",
    "answer":"[answer]"},
    ]
}
"""
# 템플릿을 사용해 PromptTemplate 객체를 생성합니다.
prompt_templet = ChatPromptTemplate.from_messages([("system", system_template), ("user", "{script_text}")])

## 파서와 모델, 템플릿 체인 연결
parser = StrOutputParser()
chain = prompt_templet | model | parser

encoding = tiktoken.encoding_for_model('gpt-3.5-turbo-16k')

def generate_lecture_notes(processed_script):
    print('generate_lecture_notes')
    # 전처리된 스크립트를 기반으로 강의 노트를 생성하는 함수입니다.
    responses = []
    split_script = split_prompt(processed_script)

    # LangChain을 사용해 GPT-3.5 모델에 요청을 보냅니다.
    for part in split_script:
        try:
            print("****************************************************************")
            print("강의 노트 생성 파트 ")
            print("****************************************************************")
            prompt = prompt_templet.format(format = json_format, script_text = part)
            print("****************프롬프트*****************")
            print(prompt)
            response = chain.invoke({"format": json_format, "script_text": part})
            print("****************응답*****************")
            print(response)
            responses.append(response)
        except Exception as e:
            print(e)
            return None
    json_dicts = [json.loads(json_str) for json_str in responses]
    merged_data = merge_json_dicts(*json_dicts)

    merged_json_str = json.dumps(merged_data, ensure_ascii=False, indent=2)
    return merged_json_str


def merge_json_dicts(*json_dicts):
    if not json_dicts:
        return {}

    # 초기 JSON 객체로 리스트의 첫 번째 요소를 사용합니다.
    merged_json = json_dicts[0]

    # 나머지 JSON 객체들을 순차적으로 병합합니다.
    for json_obj in json_dicts[1:]:
        merged_json = merge_two_json_objects(merged_json, json_obj)

    return merged_json


def merge_two_json_objects(json1, json2):
    merged_json = {}

    for key in json1.keys():
        if isinstance(json1[key], list):
            merged_json[key] = json1[key] + json2.get(key, [])
        else:
            merged_json[key] = json1[key]

    for key in json2.keys():
        if key not in merged_json:
            if isinstance(json2[key], list):
                merged_json[key] = json2[key]
            else:
                merged_json[key] = json2[key]

    return merged_json


def split_prompt(prompt, max_tokens=5500):
    print('split_prompt note')
    lines = prompt.split('\n')

    # 각 줄의 토큰 수를 미리 계산
    line_tokens = [encoding.encode(line) for line in lines]
    total_tokens = sum(len(tokens) for tokens in line_tokens)

    # 필요한 블록 수 계산
    num_blocks = (total_tokens // max_tokens) + (1 if total_tokens % max_tokens != 0 else 0)
    avg_tokens_per_block = total_tokens // num_blocks

    blocks = []
    current_block = []
    current_tokens = 0

    for i, tokens in enumerate(line_tokens):
        if current_tokens + len(tokens) > avg_tokens_per_block and len(blocks) < num_blocks - 1:
            blocks.append('\n'.join(current_block))
            current_block = []
            current_tokens = 0

        current_block.append(lines[i])
        current_tokens += len(tokens)

    if current_block:
        blocks.append('\n'.join(current_block))

    # 블록 재분할을 통해 모든 블록의 크기를 균일하게 조정
    final_blocks = []
    while len(blocks) > num_blocks:
        largest_block = max(blocks, key=lambda x: len(encoding.encode(x)))
        blocks.remove(largest_block)
        split_index = len(largest_block) // 2
        final_blocks.append(largest_block[:split_index])
        final_blocks.append(largest_block[split_index:])
    final_blocks.extend(blocks)

    return final_blocks
