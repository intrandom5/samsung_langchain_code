import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from tools import run_python

model = ChatOpenAI(
    model=os.getenv("model"),
    api_key=os.getenv("credential_key"),
    temperature=0.7,
)

SYSTEM_PROMPT = """당신은 데이터 분석 전문가 AI입니다.
사용자의 질문에 답하기 위해 Python 코드(pandas, matplotlib)를 작성하고
run_python 도구로 실행한 뒤, 결과를 바탕으로 인사이트를 한국어로 설명하세요.

규칙:
- `df` 변수에 사용자의 데이터가 로드되어 있습니다.
- 수치 결과는 반드시 print()로 출력하세요.
- 시각화가 필요하면 matplotlib 코드를 작성하고 plt.show()를 호출하세요.
- 코드 자체를 장황하게 설명하지 말고, 실행 결과와 인사이트를 설명하세요."""

agent = create_agent(
    model,
    tools=[run_python],
    system_prompt=SYSTEM_PROMPT,
    checkpointer=InMemorySaver(),
)
