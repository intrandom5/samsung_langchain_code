import os
from dotenv import load_dotenv
from middleware import logging_middleware

from langchain.tools import tool
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model


# .env 파일로부터 api_key를 불러오는 코드
load_dotenv(dotenv_path=".env")

# 모델 이름
model_name = "gpt-5.4-mini"

# LLM 정의
model = init_chat_model(
    model=model_name,
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.7,
)

grammer_agent = create_agent(
    model,
    system_prompt="당신은 10년차 경력의 편집장입니다. 입력 받은 텍스트의 문법적 오류만 집중적으로 찾아서 수정하고 피드백 해주세요",
    tools=[],
)

content_agent = create_agent(
    model,
    system_prompt="당신은 보고서 작성의 달인입니다. 보고서를 보고 내용 상 문제되는 부분이 있는지만 집중적으로 체크하고 피드백 해주세요.",
    tools=[],
)

format_agent = create_agent(
    model,
    system_prompt="당신은 보고서 양식 검토기입니다. 보고서를 보고 양식 상 잘못된 부분이 있는지만 집중적으로 체크하고 피드백 해주세요.",
    tools=[],
)