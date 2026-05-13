"""
[Step 7] 도구 호출 시각화 (최종 완성본)

새로 배우는 것:
    - st.info     : 파란색 정보 알림 박스
    - st.error    : 빨간색 오류 알림 박스
    - st.expander : 접고 펼칠 수 있는 섹션 컨테이너
    - st.code     : 코드 블록 형태로 텍스트를 표시 (language=None이면 일반 텍스트)
"""
import sys
import os
import uuid
import streamlit as st
from langchain_core.messages import AIMessageChunk, ToolMessage

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

st.set_page_config(page_title="Step 7 - 도구 시각화", page_icon="🔧", layout="wide")

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

    if "thread_id" in st.session_state:
        st.caption(f"세션 ID: `{st.session_state.thread_id[:8]}...`")

# ── 세션 상태 초기화 ───────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

# ── 메인 영역 ─────────────────────────────────────────────────────────────────
st.title("💬 AI 어시스턴트")

if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown(
            "안녕하세요! 키키테크 AI 어시스턴트입니다. 오늘은 무엇을 도와드릴까요?  \n"
            "계산, 위키피디아 검색, 키키테크 내부 문서 검색 등을 도와드릴 수 있습니다."
        )

# 대화 기록 표시 (도구 사용 내역 포함)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("tools"):
            # ── st.expander ────────────────────────────────────────────────────
            # 기본적으로 접혀 있고, 클릭하면 내용이 펼쳐지는 섹션입니다.
            with st.expander(f"🔧 도구 사용 내역 ({len(msg['tools'])}건)"):
                for i, tool in enumerate(msg["tools"]):
                    if i > 0:
                        st.divider()
                    st.markdown(f"**도구:** `{tool['name']}`")
                    result = tool["result"]
                    # ── st.code ────────────────────────────────────────────────
                    # 코드 블록 스타일로 텍스트를 표시합니다.
                    # language=None 이면 구문 강조 없이 표시합니다.
                    st.code(
                        result[:800] + ("..." if len(result) > 800 else ""),
                        language=None
                    )

if prompt := st.chat_input("메시지를 입력하세요..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        agent = load_agent()
        text_placeholder = st.empty()
        tool_indicator = st.empty()   # 도구 실행 중 알림용 placeholder
        full_response = ""
        tool_results = []

        try:
            for chunk, _ in agent.stream(
                {"messages": {"role": "user", "content": prompt}},
                {"configurable": {"thread_id": st.session_state.thread_id}},
                stream_mode="messages"
            ):
                if isinstance(chunk, AIMessageChunk):
                    # 도구 호출이 시작되는 시점을 감지해 알림을 표시합니다.
                    if getattr(chunk, "tool_call_chunks", None):
                        for tc in chunk.tool_call_chunks:
                            if tc.get("name"):
                                # ── st.info ────────────────────────────────────
                                # 파란색 정보 박스를 표시합니다.
                                tool_indicator.info(f"🔧 `{tc['name']}` 도구 실행 중...")
                    if chunk.content:
                        full_response += chunk.content
                        text_placeholder.markdown(full_response + "▌")

                elif isinstance(chunk, ToolMessage):
                    tool_indicator.empty()   # 도구 완료 시 알림 제거
                    tool_results.append({
                        "name": chunk.name or "tool",
                        "result": chunk.content
                    })

            tool_indicator.empty()
            text_placeholder.markdown(full_response or "처리가 완료되었습니다.")

            if tool_results:
                with st.expander(f"🔧 도구 사용 내역 ({len(tool_results)}건)"):
                    for i, tool in enumerate(tool_results):
                        if i > 0:
                            st.divider()
                        st.markdown(f"**도구:** `{tool['name']}`")
                        result = tool["result"]
                        st.code(
                            result[:800] + ("..." if len(result) > 800 else ""),
                            language=None
                        )

        except Exception as e:
            tool_indicator.empty()
            # ── st.error ───────────────────────────────────────────────────────
            # 빨간색 오류 박스를 표시합니다.
            text_placeholder.error(f"오류가 발생했습니다: {e}")
            full_response = f"오류가 발생했습니다: {e}"

    saved_msg = {
        "role": "assistant",
        "content": full_response or "처리가 완료되었습니다."
    }
    if tool_results:
        saved_msg["tools"] = tool_results
    st.session_state.messages.append(saved_msg)
