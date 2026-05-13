"""
Step 3: RAG 문서 검색 도구 추가
=================================
step2의 스케줄 에이전트에 사내 문서 검색 기능을 추가합니다.
"연차 신청은 어떻게 해?", "현재 진행 중인 프로젝트가 뭐야?" 같은 질문도 처리합니다.

실행:
    streamlit run step3_rag.py

🆕 이 단계에서 새로 배우는 것 (두 가지):

    1. 에이전트에 도구를 추가하는 것만으로 기능이 확장됩니다.
       load_agent()의 tools=[] 리스트에 search_documents를 추가하면 끝입니다.
       에이전트 코드 나머지는 step2와 똑같습니다.

    2. FAISS 벡터스토어(무거운 초기화)를 @st.cache_resource로 분리합니다.
       에이전트와 별개로 캐싱해야 하는 이유:
       - load_agent()는 이미 cache_resource로 한 번만 실행됩니다.
       - 하지만 벡터스토어 빌드(문서 파싱 + 임베딩 API 호출)는 특히 무겁습니다.
       - 가독성을 위해 load_vectorstore()와 load_agent()를 분리합니다.

⚠️ 첫 실행 시: 문서 임베딩 생성에 10~30초가 걸릴 수 있습니다. (이후 실행은 캐시 사용)
"""
import os
import uuid
from datetime import date

import streamlit as st
from dotenv import load_dotenv, find_dotenv
from langchain_core.messages import AIMessageChunk, ToolMessage

load_dotenv(find_dotenv())

st.set_page_config(page_title="키키테크 업무 도우미", page_icon="🏢", layout="wide")
st.title("🏢 키키테크 업무 도우미 — Step 3")
st.caption("스케줄 관리 + 사내 문서 Q&A (RAG)")

# ═══════════════════════════════════════════════════════════════════════════════
# 🆕 [핵심 1] 벡터스토어 초기화 — 에이전트와 분리해서 캐싱
# ═══════════════════════════════════════════════════════════════════════════════
@st.cache_resource(show_spinner="📚 사내 문서를 로딩 중입니다... (첫 실행 시 약 30초)")
def load_vectorstore():
    """
    docs/ 폴더의 문서 4종을 파싱하고 FAISS 벡터스토어를 구축합니다.
    @st.cache_resource 덕분에 앱을 새로고침해도 재실행되지 않습니다.
    """
    from tools.rag_tool import build_vectorstore

    # 이 파일 기준으로 docs/ 폴더 경로를 계산합니다
    docs_dir = os.path.join(os.path.dirname(__file__), "docs")
    return build_vectorstore(docs_dir)


# ═══════════════════════════════════════════════════════════════════════════════
# 🆕 [핵심 2] 에이전트 — 기존 도구 4개 + search_documents 1개 추가
# ═══════════════════════════════════════════════════════════════════════════════
@st.cache_resource
def load_agent():
    """
    스케줄 도구 4개 + RAG 검색 도구 1개 = 총 5개 도구를 가진 에이전트를 생성합니다.

    🆕 포인트: step2 대비 바뀐 것은 딱 두 가지입니다.
        1. load_vectorstore()로 벡터스토어를 가져옴
        2. create_search_tool(vs)로 만든 도구를 tools=[] 리스트에 추가
    """
    from langchain_openai import ChatOpenAI
    from langchain.agents import create_agent
    from langgraph.checkpoint.memory import InMemorySaver
    from tools.schedule_tools import (
        add_schedule, get_schedules, list_all_schedules, delete_schedule
    )
    from tools.rag_tool import create_search_tool

    today_str = date.today().strftime("%Y-%m-%d")
    system_prompt = f"""당신은 키키테크의 AI 업무 도우미입니다.

오늘 날짜: {today_str}

## 사용 가능한 도구
- **일정 관리**: add_schedule / get_schedules / list_all_schedules / delete_schedule
- **문서 검색**: search_documents — 회사 소개, 제품 카탈로그, 사내 규정, 임직원/프로젝트 현황

## 도구 선택 기준
- 일정 추가/조회/삭제 요청 → 스케줄 도구 사용
- 회사/제품/규정/직원 관련 질문 → search_documents 사용
- 두 가지를 함께 요청하면 순서대로 처리

날짜는 YYYY-MM-DD, 시간은 HH:MM 형식으로 저장하세요.
항상 한국어로 친절하게 답변하세요."""

    model = ChatOpenAI(
        model=os.getenv("model"),
        api_key=os.getenv("credential_key"),
        temperature=0.7,
    )

    # 벡터스토어를 주입해서 search_documents 도구를 생성합니다
    vs = load_vectorstore()
    search_documents = create_search_tool(vs)

    return create_agent(
        model,
        # 🆕 스케줄 도구 4개 + RAG 도구 1개
        tools=[add_schedule, get_schedules, list_all_schedules, delete_schedule, search_documents],
        system_prompt=system_prompt,
        checkpointer=InMemorySaver(),
    )


# ── 사이드바 ──────────────────────────────────────────────────────────────────
import json

def _get_today_schedules() -> list[dict]:
    data_path = os.path.join(os.path.dirname(__file__), "data", "schedules.json")
    if not os.path.exists(data_path):
        return []
    with open(data_path, "r", encoding="utf-8") as f:
        all_schedules = json.load(f)
    today_str = date.today().strftime("%Y-%m-%d")
    today = [s for s in all_schedules if s["date"] == today_str]
    return sorted(today, key=lambda x: x["time"])


with st.sidebar:
    st.header("📅 오늘 일정")
    st.caption(date.today().strftime("%Y년 %m월 %d일"))

    for s in _get_today_schedules():
        with st.container(border=True):
            st.markdown(f"**{s['time']}** {s['title']}")
            if s["description"]:
                st.caption(s["description"])
            st.caption(f"ID: `{s['id']}`")

    if not _get_today_schedules():
        st.info("오늘 일정이 없습니다.")

    st.divider()
    if st.button("🗑️ 대화 초기화", use_container_width=True):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()

    st.divider()
    st.markdown("**💬 질문 예시**")
    st.markdown("""
    **📅 일정 관리**
    - 오늘 오후 2시 팀 미팅 추가해줘
    - 이번 주 일정 보여줘

    **📋 사내 문서 Q&A**
    - 연차 신청 절차가 어떻게 돼?
    - 키키테크 주요 제품이 뭐야?
    - 현재 진행 중인 프로젝트 알려줘

    **🔀 복합 요청**
    - 행동강령에서 복장 규정 찾아보고, 내일 복장 점검 일정도 추가해줘
    """)

# ── session_state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

# ── 대화 표시 ─────────────────────────────────────────────────────────────────
if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown(
            "안녕하세요! 키키테크 AI 업무 도우미입니다. 🏢\n\n"
            "**일정 관리**와 **사내 문서 검색** 모두 도와드릴 수 있습니다!\n\n"
            "_(첫 질문 전에 문서 로딩이 완료될 때까지 잠시 기다려 주세요)_"
        )

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── 채팅 입력 처리 ────────────────────────────────────────────────────────────
if prompt := st.chat_input("일정이나 사내 규정에 대해 물어보세요..."):

    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        placeholder = st.empty()
        tool_status = st.empty()
        full_response = ""

        for chunk, _ in load_agent().stream(
            {"messages": {"role": "user", "content": prompt}},
            {"configurable": {"thread_id": st.session_state.thread_id}},
            stream_mode="messages",
        ):
            if isinstance(chunk, AIMessageChunk):
                if getattr(chunk, "tool_call_chunks", None):
                    for tc in chunk.tool_call_chunks:
                        if tc.get("name"):
                            tool_status.info(f"🔧 {tc['name']} 실행 중...")
                if chunk.content:
                    full_response += chunk.content
                    placeholder.markdown(full_response + "▌")
            elif isinstance(chunk, ToolMessage):
                tool_status.empty()

        tool_status.empty()
        placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.rerun()
