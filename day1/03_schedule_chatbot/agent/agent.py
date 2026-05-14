import os
import uuid
from datetime import date
from dotenv import load_dotenv, find_dotenv

# 프로젝트 루트의 .env 파일을 자동으로 찾아서 불러오기
load_dotenv(find_dotenv())

from .tools import add_schedule, get_schedules, list_all_schedules, delete_schedule
from .middleware import tool_logger, token_tracker

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

credential_key=os.getenv("credential_key")
send_system_name=os.getenv("send_system_name")
model_name=os.getenv("model")
api_base_url=os.getenv("api_base_url")
user_id=os.getenv("user_id")

os.environ["OPENAI_API_KEY"] = 'api_key'

llm = ChatOpenAI(
    model=model_name,
    base_url=api_base_url,
    default_headers={
        'x-dep-ticket': credential_key,
        'Send-System-Name': send_system_name,
        'User-Id': user_id,
        'User-Type': "AD_ID",
        'Prompt-Msg-Id': str(uuid.uuid4()),
        'Completion-Msg-Id': str(uuid.uuid4())
    },
    temperature=0.7,
)

# ── 시스템 프롬프트 불러오기 ──────────────────────────────────────────────────
current_dir = os.path.dirname(__file__)
with open(os.path.join(current_dir, "agents.md"), encoding="utf-8") as f:
    system_prompt = f.read()

# 오늘 날짜를 프롬프트에 삽입 → LLM이 "내일", "다음 주" 등 상대 날짜를 계산할 수 있게
today_str = date.today().strftime("%Y-%m-%d")
system_prompt = system_prompt.replace("{today}", today_str)

# ── 에이전트 생성 ─────────────────────────────────────────────────────────────
agent = create_agent(
    llm,
    tools=[add_schedule, get_schedules, list_all_schedules, delete_schedule],
    system_prompt=system_prompt,
    middleware=[tool_logger, token_tracker],
    checkpointer=InMemorySaver(),  # 대화 메모리 (프로그램 종료 시 초기화됨)
)
