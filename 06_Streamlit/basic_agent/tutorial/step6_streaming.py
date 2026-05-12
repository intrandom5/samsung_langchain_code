"""
[Step 6] 실시간 스트리밍 출력

Step 5는 에이전트가 응답을 완전히 생성한 후에야 화면에 표시했습니다.
이번 단계에서는 토큰이 생성되는 즉시 화면에 표시합니다.

새로 배우는 것:
    - st.empty : 나중에 내용을 채울 수 있는 빈 자리표시자(placeholder)를 만듭니다.
                 .markdown(), .write() 등을 호출할 때마다 내용을 덮어씁니다.
                 스트리밍처럼 내용이 계속 바뀌는 상황에 사용합니다.
"""
import sys
import os
import uuid
import streamlit as st
from langchain_core.messages import AIMessageChunk

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

st.set_page_config(page_title="Step 6 - 스트리밍", page_icon="⚡", layout="wide")

@st.cache_resource
def load_agent():
    from agent.agent import agent
    return agent

# ── 사이드바 ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🤖 키키테크\nAI 어시스턴트")
    st.divider()

    st.markdown("### 🛠️ 사용 가능한 도구")
    tools_info = [
        ("🔢", "계산기",         "수학 계산 수행"),
        ("🌐", "위키피디아 검색", "사실 정보 검색"),
        ("💾", "정보 저장",       "사용자 프로필 저장"),
        ("📂", "정보 불러오기",   "저장된 프로필 조회"),
        ("📚", "문서 검색",       "키키테크 내부 문서"),
    ]
    for emoji, name, desc in tools_info:
        st.markdown(f"{emoji} **{name}**  \n&nbsp;&nbsp;&nbsp;&nbsp;*{desc}*")

    st.divider()
    if st.button("🗑️ 대화 초기화", use_container_width=True):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()

# ── 세션 상태 초기화 ───────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

# ── 메인 영역 ─────────────────────────────────────────────────────────────────
st.title("💬 AI 어시스턴트")

if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown("안녕하세요! 무엇을 도와드릴까요?")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("메시지를 입력하세요..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        agent = load_agent()

        # ── st.empty 사용법 ────────────────────────────────────────────────────
        # placeholder를 먼저 만들어 두고,
        # 토큰이 도착할 때마다 .markdown()으로 내용을 덮어씁니다.
        text_placeholder = st.empty()
        full_response = ""

        for chunk, _ in agent.stream(
            {"messages": {"role": "user", "content": prompt}},
            {"configurable": {"thread_id": st.session_state.thread_id}},
            stream_mode="messages"
        ):
            if isinstance(chunk, AIMessageChunk) and chunk.content:
                full_response += chunk.content
                # ▌ 커서를 붙여 타이핑 중임을 시각적으로 표현합니다.
                text_placeholder.markdown(full_response + "▌")

        # 스트리밍 완료 후 커서 제거
        text_placeholder.markdown(full_response or "처리가 완료되었습니다.")

    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response or "처리가 완료되었습니다."
    })
