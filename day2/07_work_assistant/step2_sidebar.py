"""
Step 2: 사이드바에 오늘 일정 실시간 반영
==========================================
step1에서 에이전트가 일정을 추가/삭제하면 채팅으로만 결과를 알 수 있었습니다.
이 단계에서는 사이드바가 항상 최신 오늘 일정을 표시하도록 만듭니다.

실행:
    streamlit run step2_sidebar.py

🆕 이 단계에서 새로 배우는 것:
    에이전트가 도구(add_schedule, delete_schedule)를 실행해서 데이터가 변경되면,
    채팅 응답이 끝난 뒤 st.rerun()을 호출해 사이드바를 자동으로 갱신하는 패턴.

    핵심 아이디어:
        1. 사이드바는 schedules.json을 직접 읽어서 오늘 일정을 표시
        2. 에이전트 응답 완료 후 st.rerun() → 스크립트 재실행 → 사이드바 갱신

    이 패턴은 "에이전트 응답이 외부 데이터를 바꿨을 때 UI에 즉시 반영"하는
    일반적인 방법입니다.
"""
import json
import os
import uuid
from datetime import date

import streamlit as st
from dotenv import load_dotenv, find_dotenv
from langchain_core.messages import AIMessageChunk, ToolMessage

load_dotenv(find_dotenv())

st.set_page_config(page_title="키키테크 업무 도우미", page_icon="📅", layout="wide")
st.title("📅 키키테크 업무 도우미 — Step 2")
st.caption("사이드바에 오늘 일정 실시간 반영")

# ─── 에이전트 초기화 (step1과 동일) ────────────────────────────────────────────
@st.cache_resource
def load_agent():
    from langchain_openai import ChatOpenAI
    from langchain.agents import create_agent
    from langgraph.checkpoint.memory import InMemorySaver
    from tools.schedule_tools import (
        add_schedule, get_schedules, list_all_schedules, delete_schedule
    )

    today_str = date.today().strftime("%Y-%m-%d")
    system_prompt = f"""당신은 키키테크의 일정 관리 AI 어시스턴트입니다.

오늘 날짜: {today_str}

## 도구 사용 규칙
- 일정 추가 → add_schedule
- 특정 날짜 조회 → get_schedules
- 전체 일정 조회 → list_all_schedules
- 일정 삭제 → delete_schedule (ID 없으면 먼저 조회)

날짜: YYYY-MM-DD / 시간: HH:MM 형식으로 저장하세요.
"내일", "다음 주 월요일" 등은 오늘 날짜 기준으로 계산하세요."""

    os.environ["OPENAI_API_KEY"] = 'api_key'
    llm = ChatOpenAI(
        model=os.getenv("model"),
        base_url=os.getenv("api_base_url"),
        default_headers={
            'x-dep-ticket': os.getenv("credential_key"),
            'Send-System-Name': os.getenv("send_system_name"),
            'User-Id': os.getenv("user_id"),
            'User-Type': "AD_ID",
            'Prompt-Msg-Id': str(uuid.uuid4()),
            'Completion-Msg-Id': str(uuid.uuid4())
        },
        temperature=0.7,
    )
    return create_agent(
        llm,
        tools=[add_schedule, get_schedules, list_all_schedules, delete_schedule],
        system_prompt=system_prompt,
        checkpointer=InMemorySaver(),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 🆕 [핵심] 사이드바: schedules.json을 직접 읽어서 오늘 일정 표시
# ═══════════════════════════════════════════════════════════════════════════════
def _get_today_schedules() -> list[dict]:
    """
    schedules.json에서 오늘 날짜의 일정만 읽어서 반환합니다.

    사이드바는 에이전트를 통하지 않고 JSON을 직접 읽습니다.
    → 에이전트 호출 없이 빠르게 현재 상태를 확인할 수 있습니다.
    """
    data_path = os.path.join(os.path.dirname(__file__), "data", "schedules.json")
    if not os.path.exists(data_path):
        return []
    with open(data_path, "r", encoding="utf-8") as f:
        all_schedules = json.load(f)

    today_str = date.today().strftime("%Y-%m-%d")
    today = [s for s in all_schedules if s["date"] == today_str]
    return sorted(today, key=lambda x: x["time"])  # 시간순 정렬


with st.sidebar:
    st.header("📅 오늘 일정")
    st.caption(f"{date.today().strftime('%Y년 %m월 %d일 (%A)')}")

    today_schedules = _get_today_schedules()

    if today_schedules:
        for s in today_schedules:
            # 각 일정을 카드 형태로 표시
            with st.container(border=True):
                st.markdown(f"**{s['time']}** {s['title']}")
                if s["description"]:
                    st.caption(s["description"])
                st.caption(f"ID: `{s['id']}`")
    else:
        st.info("오늘 일정이 없습니다.")

    st.divider()
    if st.button("🗑️ 대화 초기화", use_container_width=True):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()

    st.divider()
    st.markdown("**💬 질문 예시**")
    st.markdown(f"""
    - 오늘 오후 3시에 보고서 제출 추가해줘
    - 내일 오전 9시 스탠드업 미팅 잡아줘
    - 전체 일정 보여줘
    """)

# ── session_state 초기화 ──────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

# ── 기존 대화 표시 ────────────────────────────────────────────────────────────
if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown(
            f"안녕하세요! 오늘은 **{date.today().strftime('%Y년 %m월 %d일')}**입니다. 😊\n\n"
            "일정을 추가하거나 삭제하면 왼쪽 사이드바가 자동으로 업데이트됩니다!"
        )

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── 채팅 입력 처리 ────────────────────────────────────────────────────────────
if prompt := st.chat_input("일정을 말씀해주세요..."):

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

    # ═══════════════════════════════════════════════════════════════════════════
    # 🆕 [핵심] 응답 완료 후 st.rerun() 호출
    # ═══════════════════════════════════════════════════════════════════════════
    # 에이전트가 add_schedule이나 delete_schedule을 실행하면 schedules.json이 변경됩니다.
    # st.rerun()으로 스크립트를 재실행하면 _get_today_schedules()가 다시 호출되고
    # 사이드바가 최신 데이터로 갱신됩니다.
    #
    # 주의: rerun은 스크립트 전체를 다시 실행하므로, 응답이 저장된 뒤(위 append 이후)에 호출해야 합니다.
    st.rerun()
