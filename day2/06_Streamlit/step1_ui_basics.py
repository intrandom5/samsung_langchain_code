# 실행 방법: 
# day2/06_Streamlit 폴더로 이동
# conda activate llm-agent
# streamlit run step1_ui_basics.py
#
# [이번 단계에서 배울 것]
# Streamlit의 기본 UI 요소들을 살펴봅니다.
# 코드를 수정하면 저장 즉시 화면이 바뀌는 것을 확인해 보세요!

import streamlit as st

# ── 제목과 텍스트 ─────────────────────────────────────────────────────────────

st.title("안녕하세요, Streamlit!")         # 가장 큰 제목
st.header("이건 header입니다")             # 중간 제목
st.subheader("이건 subheader입니다")       # 작은 제목

st.write("st.write()는 뭐든 출력할 수 있어요.")
st.markdown("**마크다운**도 *됩니다!* `코드`도 되고요.")

st.divider()  # 구분선

# ── 입력 요소 ─────────────────────────────────────────────────────────────────

name = st.text_input("이름을 입력하세요")   # 텍스트 입력창
age  = st.number_input("나이", min_value=0, max_value=120, value=25)
lang = st.selectbox("좋아하는 언어", ["Python", "JavaScript", "Java"])

st.divider()

# ── 버튼 ─────────────────────────────────────────────────────────────────────

if st.button("제출"):
    st.write(f"이름: {name}, 나이: {age}, 언어: {lang}")
    st.success("제출 완료!")   # 초록색 메시지
    # st.error("에러!")        # 빨간색
    # st.warning("경고!")      # 노란색
    # st.info("정보!")         # 파란색
