# 실행 방법: 
# day2/06_Streamlit 폴더로 이동
# conda activate llm-agent
# 실행 방법: streamlit run step3_session_state.py
#
# [이번 단계에서 배울 것]
# Streamlit은 버튼을 클릭할 때마다 코드를 처음부터 다시 실행합니다.
# 그래서 일반 변수에 값을 저장하면 클릭할 때마다 초기화됩니다.
#
# st.session_state는 이 문제를 해결해 줍니다.
# 페이지를 새로고침해도 값이 유지되는 "기억 공간"이라고 생각하면 됩니다.

import streamlit as st

st.title("카운터 앱으로 배우는 session_state")

# ── 문제 확인: 일반 변수는 왜 안 될까? ──────────────────────────────────────

st.subheader("일반 변수 (작동 안 함)")

count_broken = 0  # 버튼 클릭마다 코드가 재실행되면서 매번 0으로 초기화됨

if st.button("일반 변수로 증가"):
    count_broken += 1

st.write(f"값: {count_broken}")  # 항상 0 또는 1

st.divider()

# ── 해결: session_state 사용 ─────────────────────────────────────────────────

st.subheader("session_state (올바른 방법)")

# session_state에 키가 없으면 초기값을 설정합니다 (최초 1회만 실행됨)
if "count" not in st.session_state:
    st.session_state.count = 0

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("➕ 증가"):
        st.session_state.count += 1

with col2:
    if st.button("➖ 감소"):
        st.session_state.count -= 1

with col3:
    if st.button("🔄 초기화"):
        st.session_state.count = 0

st.metric(label="현재 카운트", value=st.session_state.count)

# ── session_state 내부 들여다보기 ────────────────────────────────────────────

with st.expander("session_state 내부 확인"):
    st.write(dict(st.session_state))
