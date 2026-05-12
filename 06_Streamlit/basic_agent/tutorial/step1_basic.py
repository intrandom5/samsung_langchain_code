"""
[Step 1] 첫 번째 Streamlit 앱

실행 방법:
    streamlit run step1_basic.py

새로 배우는 것:
    - st.set_page_config : 브라우저 탭 제목/아이콘/레이아웃 설정
    - st.title / st.write / st.markdown / st.caption : 텍스트 출력
    - st.divider : 구분선
"""
import streamlit as st

# ── 페이지 설정 (반드시 첫 번째 st 호출이어야 함) ─────────────────────────────
st.set_page_config(
    page_title="키키테크 AI 어시스턴트",   # 브라우저 탭 제목
    page_icon="🤖",                        # 브라우저 탭 아이콘
    layout="wide"                          # "centered"(기본) 또는 "wide"
)

# ── 텍스트 출력 ────────────────────────────────────────────────────────────────
st.title("💬 AI 어시스턴트")               # 가장 큰 제목 (H1)

st.write("안녕하세요! Streamlit 첫 번째 앱입니다.") # 일반 텍스트

st.markdown("**굵게**, *기울임*, `인라인 코드`도 사용할 수 있습니다.") # 굵게, 기울임, 인라인 코드 등을 쓰고 싶을 때

st.divider()                               # 가로 구분선

st.caption("st.caption은 작은 보조 텍스트에 사용합니다.") # 작은 보조 텍스트
