import os
import uuid
from dotenv import load_dotenv, find_dotenv

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver

from .tools import search_employee, search_product, search_policy
from .middleware import tool_logger, token_tracker, guardrail

load_dotenv(find_dotenv())

credential_key = os.getenv("credential_key")
send_system_name = os.getenv("send_system_name")
model_name = os.getenv("model")
api_base_url = os.getenv("api_base_url")
user_id = os.getenv("user_id")

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

# ── Sub-agent 정의 ────────────────────────────────────────────────────────────



# ── Sub-agent를 tool로 감싸기 ─────────────────────────────────────────────────



# ── 시스템 프롬프트 불러오기 ──────────────────────────────────────────────────



# ── Supervisor Agent 생성 ─────────────────────────────────────────────────────

