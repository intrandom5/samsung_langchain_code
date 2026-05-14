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

model = ChatOpenAI(
    model=model_name,
    base_url=api_base_url,
    default_headers={
        'x-dep-ticekt': credential_key,
        'Send-System-Name': send_system_name,
        'User-Id': user_id,
        'User-Type': "AD_ID",
        'Prompt-Msg-Id': str(uuid.uuid4()),
        'Completion-Msg-Id': str(uuid.uuid4())
    },
    temperature=0.7,
)

# ── Sub-agent 정의 ────────────────────────────────────────────────────────────

employee_agent = create_agent(
    model,
    tools=[search_employee],
    system_prompt="당신은 키키테크 임직원 정보 전문 에이전트입니다. 임직원의 이름을 파악해서 search_employee 도구로 정보를 찾아 답변하세요.",
)

product_agent = create_agent(
    model,
    tools=[search_product],
    system_prompt="당신은 키키테크 제품 전문 에이전트입니다. search_product 도구로 제품 정보를 찾아 답변하세요.",
)

policy_agent = create_agent(
    model,
    tools=[search_policy],
    system_prompt="당신은 키키테크 사내 규정 전문 에이전트입니다. search_policy 도구로 규정을 찾아 답변하세요.",
)

# ── Sub-agent를 tool로 감싸기 ─────────────────────────────────────────────────

@tool
def ask_employee_agent(query: str) -> str:
    """임직원 이름, 연락처, 부서, 담당업무, 프로젝트 현황 등 직원 관련 질문을 처리합니다."""
    result = employee_agent.invoke({"messages": [{"role": "user", "content": query}]})
    return result["messages"][-1].content


@tool
def ask_product_agent(query: str) -> str:
    """키키테크 제품 소개, 기능, 가격, 회사 개요 등 제품과 회사 관련 질문을 처리합니다."""
    result = product_agent.invoke({"messages": [{"role": "user", "content": query}]})
    return result["messages"][-1].content


@tool
def ask_policy_agent(query: str) -> str:
    """근무 규정, 복리후생, 행동강령, 보안 정책 등 사내 규정 관련 질문을 처리합니다."""
    result = policy_agent.invoke({"messages": [{"role": "user", "content": query}]})
    return result["messages"][-1].content

# ── 시스템 프롬프트 불러오기 ──────────────────────────────────────────────────

current_dir = os.path.dirname(__file__)
with open(os.path.join(current_dir, "agents.md"), encoding="utf-8") as f:
    system_prompt = f.read()

# ── Supervisor Agent 생성 ─────────────────────────────────────────────────────

agent = create_agent(
    model,
    tools=[ask_employee_agent, ask_product_agent, ask_policy_agent],
    system_prompt=system_prompt,
    middleware=[guardrail, tool_logger, token_tracker],
    checkpointer=InMemorySaver(),
)
