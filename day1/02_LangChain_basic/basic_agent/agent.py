'''
[코드 옮길 때 주의사항]

1. .env 불러오기
    middleware에서도 요약 middleware를 사용하면서 챗봇이 필요하기 때문에 .env 파일을 먼저 불러와야 합니다!

2. tools와 middleware 불러오기
    주피터 노트북에선 같은 파일 안에서 tools와 middleware들이 정의되어 있었습니다.
    따라서 별도의 코드가 필요하지 않았지만, 현재 agent.py에는 tools와 middleware들의 코드가 존재하지 않습니다.
    그렇기 때문에 tools.py와 middleware.py에서 해당 도구들을 불러올 필요가 있습니다!
    불러오는 방법은 아래와 같습니다.
'''
import os
from dotenv import load_dotenv

# .env 파일로부터 api_key를 불러오는 코드
load_dotenv(dotenv_path=".env")

from .tools import wikipedia_search, calculator, save_user_info, load_user_info
from .middleware import logging_middleware, context_trimmer, text_summarizer

from langchain.chat_models import init_chat_model

# 모델 이름
model_name = "gpt-5.4-mini"

# LLM 정의
model = init_chat_model(
    model=model_name,
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.7,
)

# agents.md의 정확한 경로를 찾아가기 위해 현재 파일의 경로 `__file__`을 제공해 준다.
current_dir = os.path.dirname(__file__)
with open(os.path.join(current_dir, "agents.md"), encoding="utf-8") as f:
    system_prompt = f.read()

from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

agent = create_agent(
    model,
    tools=[calculator, wikipedia_search, save_user_info, load_user_info],
    middleware=[logging_middleware, context_trimmer, text_summarizer],
    system_prompt=system_prompt,
    checkpointer=InMemorySaver()
)