import streamlit as st
from langchain_core.messages import AIMessageChunk, ToolMessage
import uuid

st.set_page_config(
    page_title="키키테크 AI 어시스턴트",
    page_icon="🤖",
    layout="wide"
)

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
        ("🔢", "계산기", "수학 계산 수행"),
        ("🌐", "위키피디아 검색", "사실 정보 검색"),
        ("💾", "정보 저장", "사용자 프로필 저장"),
        ("📂", "정보 불러오기", "저장된 프로필 조회"),
        ("📚", "문서 검색", "키키테크 내부 문서"),
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

# ── 헤더 ──────────────────────────────────────────────────────────────────────
st.title("💬 AI 어시스턴트")

# ── 초기 인사 ─────────────────────────────────────────────────────────────────
if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown(
            "안녕하세요! 키키테크 AI 어시스턴트입니다. 오늘은 무엇을 도와드릴까요?  \n"
            "계산, 위키피디아 검색, 키키테크 내부 문서 검색 등을 도와드릴 수 있습니다."
        )

# ── 대화 히스토리 표시 ────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("tools"):
            with st.expander(f"🔧 도구 사용 내역 ({len(msg['tools'])}건)"):
                for i, tool in enumerate(msg["tools"]):
                    if i > 0:
                        st.divider()
                    st.markdown(f"**도구:** `{tool['name']}`")
                    result = tool["result"]
                    st.code(
                        result[:800] + ("..." if len(result) > 800 else ""),
                        language=None
                    )

# ── 채팅 입력 및 응답 ─────────────────────────────────────────────────────────
if prompt := st.chat_input("메시지를 입력하세요..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        agent = load_agent()
        text_placeholder = st.empty()
        tool_indicator = st.empty()
        full_response = ""
        tool_results = []

        try:
            for chunk, metadata in agent.stream(
                {"messages": {"role": "user", "content": prompt}},
                {"configurable": {"thread_id": st.session_state.thread_id}},
                stream_mode="messages"
            ):
                if isinstance(chunk, AIMessageChunk):
                    # 도구 호출 시작 표시
                    if getattr(chunk, "tool_call_chunks", None):
                        for tc in chunk.tool_call_chunks:
                            if tc.get("name"):
                                tool_indicator.info(f"🔧 `{tc['name']}` 도구 실행 중...")
                    # 텍스트 스트리밍
                    if chunk.content:
                        full_response += chunk.content
                        text_placeholder.markdown(full_response + "▌")

                elif isinstance(chunk, ToolMessage):
                    tool_indicator.empty()
                    tool_results.append({
                        "name": chunk.name or "tool",
                        "result": chunk.content
                    })

            # 최종 응답 확정
            tool_indicator.empty()
            text_placeholder.markdown(full_response or "처리가 완료되었습니다.")

            # 도구 사용 결과 표시
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
            error_msg = str(e)
            text_placeholder.error(f"오류가 발생했습니다: {error_msg}")
            full_response = f"오류가 발생했습니다: {error_msg}"

    # 세션에 저장
    saved_msg = {
        "role": "assistant",
        "content": full_response or "처리가 완료되었습니다."
    }
    if tool_results:
        saved_msg["tools"] = tool_results
    st.session_state.messages.append(saved_msg)
