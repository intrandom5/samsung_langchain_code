"""
CSV 데이터 분석기
실행: streamlit run app.py
"""
import base64
import uuid

import pandas as pd
import streamlit as st
from langchain_core.messages import AIMessageChunk, ToolMessage

st.set_page_config(page_title="CSV 분석기", page_icon="📊", layout="wide")
st.title("📊 CSV 데이터 분석기")
st.caption("CSV 파일을 업로드하고 AI에게 데이터 분석을 요청하세요.")


@st.cache_resource
def load_agent():
    """에이전트를 한 번만 로드합니다 (매 새로고침마다 재생성 방지)."""
    from agent import agent
    return agent


# ── 파일 업로드 ────────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader("CSV 파일 선택", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    from tools import set_dataframe, get_figure
    set_dataframe(df)  # 도구에 DataFrame 전달

    # ── 기본 정보 ──────────────────────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    c1.metric("행 수", f"{len(df):,}")
    c2.metric("열 수", len(df.columns))
    c3.metric("결측치", int(df.isnull().sum().sum()))

    with st.expander("📋 데이터 미리보기"):
        st.dataframe(df.head(20), use_container_width=True)

    st.divider()

    # ── 사이드바 ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.header("⚙️ 설정")
        if "thread_id" not in st.session_state:
            st.session_state.thread_id = str(uuid.uuid4())
        if st.button("🗑️ 대화 초기화", use_container_width=True):
            st.session_state.messages = []
            st.session_state.thread_id = str(uuid.uuid4())
            st.rerun()
        st.divider()
        st.markdown("**질문 예시**")
        st.markdown("""
- 각 컬럼의 기본 통계를 보여줘
- 결측치가 있는 컬럼은 어디야?
- 숫자형 컬럼 분포를 히스토그램으로 보여줘
- 컬럼 간 상관관계를 히트맵으로 그려줘
- 가장 값이 큰 상위 5개 행 보여줘
        """)

    # ── 채팅 인터페이스 ────────────────────────────────────────────────────────
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if not st.session_state.messages:
        with st.chat_message("assistant"):
            st.markdown(
                f"데이터를 불러왔습니다! ({len(df)}행 x {len(df.columns)}열)  \n"
                "분석하고 싶은 내용을 자유롭게 말씀해주세요."
            )

    # 대화 기록 표시
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("figure"):
                st.image(base64.b64decode(msg["figure"]))

    # 채팅 입력 및 응답
    if prompt := st.chat_input("분석 요청을 입력하세요..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            tool_indicator = st.empty()
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
                                tool_indicator.info("🔧 Python 코드 실행 중...")
                    if chunk.content:
                        full_response += chunk.content
                        placeholder.markdown(full_response + "▌")
                elif isinstance(chunk, ToolMessage):
                    tool_indicator.empty()

            tool_indicator.empty()
            placeholder.markdown(full_response)

            # 생성된 차트가 있으면 표시
            fig_b64 = get_figure()
            if fig_b64:
                st.image(base64.b64decode(fig_b64))

        # 메시지 저장 (차트 포함)
        saved_msg = {"role": "assistant", "content": full_response}
        if fig_b64:
            saved_msg["figure"] = fig_b64
        st.session_state.messages.append(saved_msg)

else:
    st.info("CSV 파일을 업로드하면 AI와 함께 데이터를 분석할 수 있습니다.")
    with st.expander("💡 어떻게 사용하나요?"):
        st.markdown("""
1. CSV 파일을 업로드하세요.
2. 채팅창에 분석 요청을 입력하세요.
3. AI가 Python(pandas, matplotlib) 코드를 직접 실행해 결과와 차트를 보여드립니다.
        """)
