"""
[Step 4] 사이드바 레이아웃

새로 배우는 것:
    - st.sidebar  : with 블록 안에 작성하면 사이드바에 배치됩니다.
    - st.button   : 클릭하면 True를 반환하는 버튼
    - st.rerun    : 앱을 즉시 재실행 (버튼으로 상태를 바꾼 뒤 화면 갱신할 때 사용)
"""
import streamlit as st

st.set_page_config(page_title="Step 4 - 사이드바", page_icon="🗂️", layout="wide")

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

    # 버튼: 클릭된 순간 True를 반환하고, 그 외에는 False
    if st.button("🗑️ 대화 초기화", use_container_width=True):
        st.session_state.messages = []
        st.rerun()   # session_state를 바꾼 뒤 화면을 즉시 새로 그립니다.

# ── 메인 영역 ─────────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("💬 AI 어시스턴트")

if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown("안녕하세요! 무엇을 도와드릴까요?")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("메시지를 입력하세요..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    response = f"'{prompt}'라고 하셨군요!"
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
