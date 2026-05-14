# 실행 방법: 
# day2/06_Streamlit 폴더로 이동
# conda activate llm-agent
# 실행 방법: streamlit run step2_layout.py
#
# [이번 단계에서 배울 것]
# 화면을 여러 영역으로 나누는 레이아웃 요소들을 배웁니다.

import streamlit as st

st.title("레이아웃")

# ── 사이드바 ─────────────────────────────────────────────────────────────────

st.sidebar.header("사이드바")
theme = st.sidebar.radio("테마 선택", ["라이트", "다크"])
st.sidebar.write(f"선택한 테마: {theme}")

# ── 컬럼 (화면을 나란히 나누기) ──────────────────────────────────────────────

st.subheader("columns")

col1, col2, col3 = st.columns(3)  # 3등분

with col1:
    st.write("왼쪽 컬럼")
    st.button("버튼 1")

with col2:
    st.write("가운데 컬럼")
    st.button("버튼 2")

with col3:
    st.write("오른쪽 컬럼")
    st.button("버튼 3")

st.divider()

# ── expander (접었다 펼치는 영역) ────────────────────────────────────────────

st.subheader("expander")

with st.expander("여기를 클릭하면 내용이 펼쳐집니다"):
    st.write("숨겨진 내용입니다.")
    st.write("코드나 상세 설명을 숨겨두기 좋아요.")

st.divider()

# ── 탭 ───────────────────────────────────────────────────────────────────────

st.subheader("tabs")

tab1, tab2 = st.tabs(["첫 번째 탭", "두 번째 탭"])

with tab1:
    st.write("첫 번째 탭 내용입니다.")

with tab2:
    st.write("두 번째 탭 내용입니다.")
