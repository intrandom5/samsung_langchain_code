"""
Step 4: 완성형 — 도구 시각화 + 일정 dataframe
================================================
step3의 기능을 유지하면서 UX를 완성합니다.

실행:
    streamlit run step4_complete.py

🆕 이 단계에서 새로 배우는 것 (두 가지):

    1. 도구 호출 과정을 st.expander()로 시각화합니다 (← tutorial/step7 패턴).
       사용자가 "AI가 어떤 도구를 썼는지, 결과는 뭔지" 확인할 수 있습니다.

    2. 사이드바의 오늘 일정을 st.dataframe()으로 표시합니다.
       단순 텍스트 목록 대신 표 형태로 보여줘서 가독성을 높입니다.
       (JSON → pandas DataFrame 변환 패턴)

Step 1~4 비교:
    step1: 에이전트 + 기본 채팅 (도구가 뭔지 안 보임)
    step2: + 사이드바 일정 실시간 갱신
    step3: + RAG 문서 검색
    step4: + 도구 호출 시각화 + 일정 dataframe (완성형)
"""
import json
import os
import uuid
from datetime import date

import pandas as pd
import streamlit as st
from dotenv import load_dotenv, find_dotenv
from langchain_core.messages import AIMessageChunk, ToolMessage

load_dotenv(find_dotenv())

st.set_page_config(page_title="키키테크 업무 도우미", page_icon="🚀", layout="wide")
st.title("🚀 키키테크 업무 도우미 — 완성형")
st.caption("일정 관리 + 사내 문서 Q&A + 도구 호출 시각화")


# ─── 초기화 (step3와 동일) ──────────────────────────────────────────────────────
@st.cache_resource(show_spinner="📚 사내 문서를 로딩 중입니다...")
def load_vectorstore():
    from tools.rag_tool import build_vectorstore
    docs_dir = os.path.join(os.path.dirname(__file__), "docs")
    return build_vectorstore(docs_dir)


@st.cache_resource
def load_agent():
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

날짜: YYYY-MM-DD / 시간: HH:MM 형식으로 저장하세요.
항상 한국어로 친절하게 답변하세요."""

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

    vs = load_vectorstore()
    search_documents = create_search_tool(vs)

    return create_agent(
        llm,
        tools=[add_schedule, get_schedules, list_all_schedules, delete_schedule, search_documents],
        system_prompt=system_prompt,
        checkpointer=InMemorySaver(),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 🆕 [핵심 1] 사이드바 일정을 st.dataframe()으로 표시
# ═══════════════════════════════════════════════════════════════════════════════
def _get_all_schedules() -> list[dict]:
    data_path = os.path.join(os.path.dirname(__file__), "data", "schedules.json")
    if not os.path.exists(data_path):
        return []
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _get_today_schedules() -> list[dict]:
    today_str = date.today().strftime("%Y-%m-%d")
    return sorted(
        [s for s in _get_all_schedules() if s["date"] == today_str],
        key=lambda x: x["time"],
    )


with st.sidebar:
    st.header("📅 오늘 일정")
    st.caption(date.today().strftime("%Y년 %m월 %d일"))

    today_schedules = _get_today_schedules()

    if today_schedules:
        # 🆕 JSON 리스트를 DataFrame으로 변환해서 표 형태로 표시합니다
        df = pd.DataFrame(today_schedules)[["time", "title", "description", "id"]]
        df.columns = ["시간", "제목", "설명", "ID"]
        # hide_index=True: 왼쪽의 0, 1, 2... 숫자 인덱스를 숨깁니다
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("오늘 일정이 없습니다.")

    st.divider()

    # 전체 일정 수 표시
    all_schedules = _get_all_schedules()
    st.metric("전체 등록 일정", f"{len(all_schedules)}건")

    st.divider()
    if st.button("🗑️ 대화 초기화", use_container_width=True):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()

    st.divider()
    st.markdown("**💬 질문 예시**")
    st.markdown("""
    **📅 일정**
    - 오늘 오후 4시 코드 리뷰 추가해줘
    - 이번 주 일정 보여줘

    **📋 문서 검색**
    - 키키테크의 AI 제품이 뭐가 있어?
    - 연차 신청 절차 알려줘
    - 현재 임직원 현황 알려줘

    **🔀 복합**
    - 내일 오전 신규 직원 온보딩 일정 잡아줘, 행동강령도 간략히 알려줘
    """)


# ─── session_state ────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())


# ═══════════════════════════════════════════════════════════════════════════════
# 🆕 [핵심 2] 대화 기록 표시 함수 — 도구 결과(expander) 포함
# ═══════════════════════════════════════════════════════════════════════════════
def render_message(msg: dict):
    """
    저장된 메시지를 화면에 표시합니다.
    AI 메시지에는 도구 호출 결과를 expander로 함께 표시합니다.
    """
    with st.chat_message(msg["role"]):
        # 도구 실행 결과가 있으면 먼저 expander로 표시
        for tool_result in msg.get("tool_results", []):
            with st.expander(f"🔧 **{tool_result['name']}** 실행 결과", expanded=False):
                st.code(tool_result["result"], language=None)
        st.markdown(msg["content"])


if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown(
            "안녕하세요! 키키테크 AI 업무 도우미입니다. 🚀\n\n"
            "일정 관리와 사내 문서 검색을 도와드립니다. "
            "도구를 사용할 때 어떤 도구가 실행됐는지도 확인할 수 있어요!"
        )

for msg in st.session_state.messages:
    render_message(msg)


# ── 채팅 입력 처리 ────────────────────────────────────────────────────────────
if prompt := st.chat_input("일정이나 사내 규정에 대해 물어보세요..."):

    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        placeholder = st.empty()
        tool_status = st.empty()
        full_response = ""

        # 🆕 이번 응답에서 실행된 도구 결과를 수집합니다
        tool_results = []
        current_tool_name = None

        try:
            for chunk, _ in load_agent().stream(
                {"messages": {"role": "user", "content": prompt}},
                {"configurable": {"thread_id": st.session_state.thread_id}},
                stream_mode="messages",
            ):
                if isinstance(chunk, AIMessageChunk):
                    if getattr(chunk, "tool_call_chunks", None):
                        for tc in chunk.tool_call_chunks:
                            if tc.get("name"):
                                current_tool_name = tc["name"]
                                tool_status.info(f"🔧 **{current_tool_name}** 실행 중...")

                    if chunk.content:
                        full_response += chunk.content
                        placeholder.markdown(full_response + "▌")

                elif isinstance(chunk, ToolMessage):
                    # 🆕 도구 실행 완료 → expander로 결과 즉시 표시
                    tool_name = current_tool_name or "도구"
                    tool_result_text = chunk.content

                    tool_results.append({"name": tool_name, "result": tool_result_text})

                    with st.expander(f"🔧 **{tool_name}** 실행 결과", expanded=False):
                        st.code(tool_result_text, language=None)

                    tool_status.empty()
                    current_tool_name = None

        except Exception as e:
            full_response = f"오류가 발생했습니다: {e}"
            st.error(full_response)

        tool_status.empty()
        placeholder.markdown(full_response)

    # 도구 결과를 포함해서 저장 → render_message()가 다음 렌더링 때 expander로 표시
    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response,
        "tool_results": tool_results,
    })
    st.rerun()
