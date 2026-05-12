"""
[Step 3] 세션 상태로 대화 기록 유지하기

Streamlit은 사용자가 무언가를 할 때마다 스크립트 전체를 다시 실행합니다.
일반 변수는 재실행 시 초기화되므로, 대화 기록이 사라집니다.

새로 배우는 것:
    - st.session_state : 재실행해도 값이 유지되는 딕셔너리
                         딕셔너리처럼 사용하거나 속성처럼 사용할 수 있습니다.
                         예) st.session_state["key"] = value
                             st.session_state.key = value
"""
import streamlit as st

st.set_page_config(page_title="Step 3 - 세션 상태", page_icon="💾", layout="wide")
st.title("💾 세션 상태로 대화 기록 유지")

# ── session_state 초기화 ────────────────────────────────────────────────────────
# 처음 실행될 때만 초기화하고, 이후 재실행 시에는 기존 값을 유지합니다.
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── 저장된 대화 기록 전체 표시 ──────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── 새 메시지 처리 ──────────────────────────────────────────────────────────────
if prompt := st.chat_input("메시지를 입력하세요..."):
    # 1. session_state에 저장
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. 화면에 표시
    with st.chat_message("user"):
        st.markdown(prompt)

    # 3. 응답 생성 후 저장 & 표시
    response = f"'{prompt}'라고 하셨군요!"
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
