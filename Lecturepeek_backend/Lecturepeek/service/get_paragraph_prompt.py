from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import (
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate,
)
from langchain_core.output_parsers import StrOutputParser
import tiktoken

load_dotenv()
params = {
    "temperature": 0.2,  # 생성된 텍스트의 다양성 조정
    "max_tokens": 8000,  # 생성할 최대 토큰 수
}
model = ChatOpenAI(model="gpt-3.5-turbo-16k", **params)

system_template = """
    Convert scripts in lecture videos into sentences.
    Before each sentence, there should be a 'timestamp' corresponding to the subtitles.
    """

prompt_templet = ChatPromptTemplate.from_messages([("system", system_template), ("user", "{script_text}")])

## 파서와 모델, 템플릿 체인 연결
parser = StrOutputParser()
chain = prompt_templet | model | parser

encoding = tiktoken.encoding_for_model('gpt-3.5-turbo-16k')

def generate_script(processed_script):
    print('generate_script called')
    # 전처리된 스크립트를 생성하는 함수입니다.
    responses = []
    i = 0
    script_text = "\n".join(processed_script)
    split_script = split_prompt(script_text)
    for part in split_script:
        try:
            i += 1
            print(f'**part{i}**')
            prompt = prompt_templet.format(script_text=part)
            print("****************프롬프트*****************")
            print(prompt)
            response = chain.invoke({"script_text": part})
            print('********************response*********************')
            print(response)
            responses.append(response)
        except Exception as e:
            print(e)
            return None

    combined_responses = '\n'.join(responses)
    print(f"divided : {len(responses)}")
    print(combined_responses)
    return combined_responses

    # LangChain을 사용해 GPT-3.5 모델에 요청을 보냅니다.
    #try:
    #    response = chain.invoke({"script_text": script_text})
    #    return response
    #except Exception as e:
    #    print(e)
    #    return None


def split_prompt(prompt, max_tokens=7000):
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
