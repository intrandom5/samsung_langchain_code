import streamlit as st

# ── 페이지 설정 (반드시 첫 번째 st 호출이어야 함) ─────────────────────────────
st.set_page_config(
    page_title="키키테크 AI 어시스턴트",   # 브라우저 탭 제목
    page_icon="🤖",                        # 브라우저 탭 아이콘
    layout="wide"                          # "centered"(기본) 또는 "wide"
)

if "count" not in st.session_state:
    st.session_state.count = 0

if st.button("클릭"):
    st.session_state.count += 1
    print(st.session_state)

if st.button("초기화"):
    st.session_state.count = 0

st.write(st.session_state.count)