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
    translate given json value into korean
    """

prompt_templet = ChatPromptTemplate.from_messages([("system", system_template), ("user", "{script_text}")])

## 파서와 모델, 템플릿 체인 연결
parser = StrOutputParser()
chain = prompt_templet | model | parser

encoding = tiktoken.encoding_for_model('gpt-3.5-turbo-16k')

def translate_json(json_value):
    response = chain.invoke({"script_text": json_value})
    return response