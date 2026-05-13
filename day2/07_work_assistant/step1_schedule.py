"""
Step 1: 스케줄 에이전트 + 기본 채팅 UI
========================================
day1에서 터미널(CLI)로만 쓰던 스케줄 챗봇을 Streamlit 웹 앱으로 옮깁니다.

실행:
    streamlit run step1_schedule.py

🆕 이 단계에서 새로 배우는 것:
    - day1에서 만든 도구(tools/)를 아무 수정 없이 그대로 재활용하는 방법
    - CLI용 에이전트 코드를 Streamlit에 붙이는 최소한의 작업

(Streamlit 패턴 자체는 tutorial/step5~6을 참고하세요. 여기선 설명하지 않습니다)

사전 준비:
    .env 파일에 credential_key, model 설정 필요
"""
import os
import uuid
from datetime import date

import streamlit as st
from dotenv import load_dotenv, find_dotenv
from langchain_core.messages import AIMessageChunk, ToolMessage

load_dotenv(find_dotenv())

st.set_page_config(page_title="키키테크 업무 도우미", page_icon="📅", layout="wide")
st.title("📅 키키테크 업무 도우미 — Step 1")
st.caption("스케줄 관리 에이전트 + 기본 채팅 UI")

# ═══════════════════════════════════════════════════════════════════════════════
# 🆕 [핵심] 에이전트 초기화 — day1 도구를 그대로 재활용
# ═══════════════════════════════════════════════════════════════════════════════
@st.cache_resource
def load_agent():
    """
    스케줄 관리 에이전트를 초기화합니다.

    🆕 포인트: tools/schedule_tools.py는 day1의 코드 그대로입니다.
    CLI 앱이든 Streamlit 앱이든, 도구 코드는 바꿀 필요가 없습니다.
    Streamlit으로 전환할 때 바뀌는 건 "어떻게 에이전트를 호출하느냐"뿐입니다.
    """
    from langchain_openai import ChatOpenAI
    from langchain.agents import create_agent
    from langgraph.checkpoint.memory import InMemorySaver

    # day1과 동일한 도구들 — 경로만 이 프로젝트에 맞게 조정된 버전
    from tools.schedule_tools import (
        add_schedule, get_schedules, list_all_schedules, delete_schedule
    )

    model = ChatOpenAI(
        model=os.getenv("model"),
        api_key=os.getenv("credential_key"),
        temperature=0.7,
    )

    # 시스템 프롬프트에 오늘 날짜를 주입합니다 (day1 방식 그대로)
    today_str = date.today().strftime("%Y-%m-%d")
    system_prompt = f"""당신은 키키테크의 일정 관리 AI 어시스턴트입니다.

오늘 날짜: {today_str}

## 도구 사용 규칙
- 일정 **추가** → add_schedule
- 특정 날짜 **조회** → get_schedules
- **전체** 일정 조회 → list_all_schedules
- 일정 **삭제** → delete_schedule (ID 없으면 먼저 조회)

## 날짜/시간 형식
- 날짜: YYYY-MM-DD (예: {today_str})
- 시간: HH:MM (예: 14:00)
- "내일", "다음 주 월요일" 등은 오늘 날짜 기준으로 계산

항상 친절하고 간결하게 답변하세요."""

    return create_agent(
        model,
        tools=[add_schedule, get_schedules, list_all_schedules, delete_schedule],
        system_prompt=system_prompt,
        checkpointer=InMemorySaver(),
    )

# ── session_state 초기화 (← tutorial/step3 참고) ─────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

# ── 사이드바 ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ 설정")
    if st.button("🗑️ 대화 초기화", use_container_width=True):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()

    st.divider()
    st.markdown("**💬 질문 예시**")
    st.markdown(f"""
    - 오늘({date.today().strftime('%m/%d')}) 오후 2시에 팀 미팅 추가해줘
    - 내일 일정 보여줘
    - 전체 일정 조회해줘
    - [ID]번 일정 삭제해줘
    """)
    st.divider()
    st.info("Step 2에서는 사이드바에 오늘 일정이 실시간으로 표시됩니다.")

# ── 기존 대화 표시 ────────────────────────────────────────────────────────────
if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown(
            f"안녕하세요! 키키테크 일정 관리 도우미입니다. 😊\n\n"
            f"오늘은 **{date.today().strftime('%Y년 %m월 %d일')}**입니다.\n"
            "일정 추가, 조회, 삭제를 도와드릴게요!"
        )

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── 채팅 입력 처리 (← tutorial/step6 스트리밍 패턴) ─────────────────────────
if prompt := st.chat_input("일정을 말씀해주세요... (예: 내일 오전 10시 회의 추가해줘)"):

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
