"""
Step 6: 스트리밍 응답
======================
에이전트의 응답을 토큰 단위로 받아 실시간으로 화면에 표시합니다.
ChatGPT처럼 글자가 하나씩 나타나는 효과를 구현합니다.

실행 방법:
    streamlit run step6_streaming.py

📌 이번 단계에서 배우는 것:
    - agent.stream()      : 토큰이 생성될 때마다 청크(chunk)를 전달하는 스트리밍 호출
    - st.empty()          : 내용을 나중에 채울 수 있는 빈 자리(placeholder)
    - AIMessageChunk      : 스트리밍 중 AI 응답의 조각
    - ToolMessage         : 도구 실행 결과 메시지

💡 invoke vs stream 비교:
    invoke : [========== 기다림 ===========] → "전체 응답" 한 번에 표시
    stream : "안" → "안녕" → "안녕하" → ... → "안녕하세요!" 토큰마다 갱신
"""
import os
import uuid

import streamlit as st
from dotenv import load_dotenv, find_dotenv
from langchain_core.messages import AIMessageChunk, ToolMessage

load_dotenv(find_dotenv())

st.set_page_config(page_title="Step 6: 스트리밍", page_icon="⚡", layout="wide")
st.title("⚡ 스트리밍 응답 구현")

# ═══════════════════════════════════════════════════════════════════════════════
# 에이전트 초기화 (Step 5와 동일한 패턴)
# ═══════════════════════════════════════════════════════════════════════════════
@st.cache_resource
def load_agent():
    from langchain_openai import ChatOpenAI
    from langchain.agents import create_agent
    from langgraph.checkpoint.memory import InMemorySaver
    from langchain.tools import tool

    @tool
    def get_weather(city: str) -> str:
        """도시 이름을 받아서 현재 날씨 정보를 반환합니다."""
        weather_db = {
            "서울": "맑음, 기온 23°C, 습도 55%",
            "부산": "흐림, 기온 20°C, 습도 70%",
            "제주": "비, 기온 18°C, 습도 85%",
            "대전": "맑음, 기온 25°C, 습도 50%",
        }
        return weather_db.get(city, f"'{city}'의 날씨 정보를 찾을 수 없습니다.")

    @tool
    def calculate(expression: str) -> str:
        """수식 문자열을 계산합니다. 예: '2 + 3 * 4'"""
        try:
            result = eval(expression)  # noqa: S307
            return f"{expression} = {result}"
        except Exception as e:
            return f"계산 오류: {e}"

    model = ChatOpenAI(
        model=os.getenv("model", "gpt-4o-mini"),
        api_key=os.getenv("credential_key"),
        temperature=0.7,
    )

    return create_agent(
        model,
        tools=[get_weather, calculate],
        system_prompt=(
            "당신은 친절한 한국어 AI 어시스턴트입니다. "
            "날씨 조회와 계산 도구를 사용할 수 있습니다. "
            "항상 한국어로 응답하세요."
        ),
        checkpointer=InMemorySaver(),
    )

# ═══════════════════════════════════════════════════════════════════════════════
# Session State 초기화
# ═══════════════════════════════════════════════════════════════════════════════
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
    st.caption(f"thread_id: `{st.session_state.thread_id[:8]}...`")

    st.divider()
    st.markdown("**질문 예시**")
    st.markdown("""
    - 안녕! 간단히 자기소개 해줘
    - 서울 날씨 알려줘
    - 25 * 48 계산해줘
    - 서울이랑 제주 날씨 비교해서 어디가 더 좋은지 알려줘
    """)

# ═══════════════════════════════════════════════════════════════════════════════
# 스트리밍 원리 설명
# ═══════════════════════════════════════════════════════════════════════════════
with st.expander("📌 스트리밍 작동 원리 (클릭해서 펼치기)"):
    st.markdown("""
    ### agent.stream()이 반환하는 청크(chunk) 종류

    `agent.stream(..., stream_mode="messages")` 를 쓰면 `(chunk, metadata)` 튜플을 계속 yield합니다.

    | 청크 타입 | 의미 | 처리 방법 |
    |-----------|------|-----------|
    | `AIMessageChunk` | AI가 생성한 텍스트 조각 | `chunk.content`를 누적해서 화면 갱신 |
    | `AIMessageChunk` (with tool_call_chunks) | AI가 도구 호출을 결정하는 중 | 도구 호출 중 표시 |
    | `ToolMessage` | 도구 실행이 완료된 결과 | "도구 실행 완료" 표시 |

    ### st.empty() 활용법

    ```python
    placeholder = st.empty()  # 빈 자리 확보

    full_text = ""
    for chunk in stream:
        full_text += chunk.content
        placeholder.markdown(full_text + "▌")  # 계속 갱신 (▌는 커서)

    placeholder.markdown(full_text)  # 완료 후 커서 제거
    ```
    """)

# ═══════════════════════════════════════════════════════════════════════════════
# 기존 대화 표시
# ═══════════════════════════════════════════════════════════════════════════════
if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown("안녕하세요! 스트리밍 응답이 구현된 챗봇입니다. 무엇이든 물어보세요! ⚡")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ═══════════════════════════════════════════════════════════════════════════════
# 새 메시지 처리 (스트리밍)
# ═══════════════════════════════════════════════════════════════════════════════
if prompt := st.chat_input("메시지를 입력하세요..."):

    # 1. 사용자 메시지 표시 및 저장
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. AI 응답 스트리밍
    with st.chat_message("assistant"):

        # ── st.empty() : 빈 자리(placeholder) 확보 ────────────────────────────
        # 이 자리에 스트리밍 텍스트를 계속 갱신해서 넣을 것입니다
        response_placeholder = st.empty()

        # 도구 호출 중임을 알리는 표시 (도구 결과가 오면 사라짐)
        tool_indicator = st.empty()

        full_response = ""  # 지금까지 받은 텍스트를 누적할 변수

        try:
            # ── agent.stream() 호출 ─────────────────────────────────────────────
            # stream_mode="messages" : 메시지 단위로 청크를 스트리밍합니다
            # 각 이터레이션에서 (chunk, metadata) 튜플을 반환합니다
            for chunk, _metadata in load_agent().stream(
                {"messages": {"role": "user", "content": prompt}},
                {"configurable": {"thread_id": st.session_state.thread_id}},
                stream_mode="messages",
            ):
                # ── AIMessageChunk 처리 ─────────────────────────────────────────
                if isinstance(chunk, AIMessageChunk):

                    # 도구 호출 청크인지 확인 (AI가 도구를 호출하기로 결정할 때)
                    if getattr(chunk, "tool_call_chunks", None):
                        # tool_call_chunks가 있으면 AI가 도구 이름을 생성 중
                        for tc in chunk.tool_call_chunks:
                            if tc.get("name"):
                                # 어떤 도구를 호출하는지 표시
                                tool_indicator.info(f"🔧 **{tc['name']}** 도구 실행 중...")

                    # 일반 텍스트 청크 (AI의 실제 답변 내용)
                    if chunk.content:
                        full_response += chunk.content
                        # 현재까지 받은 텍스트 + "▌" 커서를 placeholder에 갱신
                        response_placeholder.markdown(full_response + "▌")

                # ── ToolMessage 처리 ────────────────────────────────────────────
                elif isinstance(chunk, ToolMessage):
                    # 도구 실행이 완료됨 → 도구 호출 중 표시를 없앰
                    tool_indicator.empty()

        except Exception as e:
            full_response = f"오류가 발생했습니다: {e}"
            st.error(full_response)

        # ── 스트리밍 완료 후 정리 ──────────────────────────────────────────────
        tool_indicator.empty()                      # 도구 표시 제거
        response_placeholder.markdown(full_response)  # 커서(▌) 없이 최종 텍스트 표시

    # 3. AI 응답 저장
    st.session_state.messages.append({"role": "assistant", "content": full_response})

st.divider()
st.caption("Step 7에서는 도구 호출 과정을 더 자세히 시각화하고, 완성형 앱을 만듭니다.")
