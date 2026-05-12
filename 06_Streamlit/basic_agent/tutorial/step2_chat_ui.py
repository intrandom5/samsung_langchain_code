"""
[Step 2] 채팅 UI 기초

새로 배우는 것:
    - st.chat_message : 말풍선 형태의 메시지 컨테이너 ("user" / "assistant")
    - st.chat_input   : 화면 하단에 고정되는 채팅 입력창

한계:
    메시지를 보내면 페이지가 다시 렌더링되면서 이전 메시지가 사라집니다.
    → Step 3에서 session_state로 해결합니다.
"""
import streamlit as st

st.set_page_config(page_title="Step 2 - 채팅 UI", page_icon="💬", layout="wide")
st.title("💬 채팅 UI 기초")

# ── chat_message ───────────────────────────────────────────────────────────────
# with 블록 안에 작성한 내용이 말풍선 안에 표시됩니다.
# "user"는 오른쪽, "assistant"는 왼쪽 아이콘으로 표시됩니다.
with st.chat_message("assistant"):
    st.markdown("안녕하세요! 무엇을 도와드릴까요?")

with st.chat_message("user"):
    st.markdown("안녕하세요!")

st.divider()

# ── chat_input ─────────────────────────────────────────────────────────────────
# 입력값이 있으면 문자열 반환, 아무것도 입력하지 않으면 None 반환
# 항상 화면의 최하단에 배치
# := (walrus operator) 를 사용해 값 확인과 변수 할당을 동시에 처리합니다.
if prompt := st.chat_input("메시지를 입력하세요..."):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        st.markdown(f"'{prompt}'라고 하셨군요!")
