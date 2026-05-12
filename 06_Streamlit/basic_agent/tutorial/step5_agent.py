"""
[Step 5] 에이전트 연결 + 캐싱

새로 배우는 것:
    - @st.cache_resource : 앱 전체에서 딱 한 번만 실행되는 함수를 만드는 데코레이터.
                           앱이 재실행되어도 반환값(에이전트, DB 연결 등)을 재사용합니다.
                           무거운 객체 초기화에 사용합니다.
    - st.spinner         : 처리 중임을 나타내는 로딩 스피너 표시

실행 방법 (tutorial 폴더에서):
    streamlit run step5_agent.py
"""
import sys
import os
import uuid
import streamlit as st
from langchain_core.messages import AIMessageChunk

# tutorial 폴더의 상위(basic_agent)를 경로에 추가해 agent 패키지를 불러올 수 있게 합니다.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

st.set_page_config(page_title="Step 5 - 에이전트 연결", page_icon="🤖", layout="wide")

# ── 에이전트 캐싱 ──────────────────────────────────────────────────────────────
# @st.cache_resource 없이 load_agent()를 쓰면 매 재실행마다 에이전트를 새로 만들어
# API 연결 비용이 발생하고 대화 기록(메모리)도 초기화됩니다.
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
    # 세션마다 고유한 ID를 부여해 에이전트 메모리를 분리합니다.
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
        # st.spinner: with 블록이 실행되는 동안 로딩 애니메이션을 표시합니다.
        with st.spinner("생각 중..."):
            agent = load_agent()
            full_response = ""
            for chunk, _ in agent.stream(
                {"messages": {"role": "user", "content": prompt}},
                {"configurable": {"thread_id": st.session_state.thread_id}},
                stream_mode="messages"
            ):
                if isinstance(chunk, AIMessageChunk) and chunk.content:
                    full_response += chunk.content

        response = full_response or "처리가 완료되었습니다."
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
