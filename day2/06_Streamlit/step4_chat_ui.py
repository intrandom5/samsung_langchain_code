# 실행 방법: 
# day2/06_Streamlit 폴더로 이동
# conda activate llm-agent
# 실행 방법: streamlit run step4_chat_ui.py
#
# [이번 단계에서 배울 것]
# 채팅 UI를 구성하고, LangChain 에이전트와 연결하는 방법을 배웁니다.
#
# [왜 Streamlit이 LangChain 에이전트 UI로 좋을까요?]
#
# 1. 코드가 짧습니다.
#    Flask/FastAPI + HTML로 만들면 수백 줄이 필요한 채팅 UI를
#    Streamlit으로는 20~30줄로 만들 수 있습니다.
#
# 2. 채팅 UI가 기본 제공됩니다.
#    st.chat_message(), st.chat_input() 두 줄이면
#    ChatGPT와 비슷한 채팅 화면이 완성됩니다.
#
# 3. 대화 기록 관리가 쉽습니다.
#    session_state에 메시지 목록을 저장하면
#    LangChain의 대화 기록과 자연스럽게 연동됩니다.

import streamlit as st

st.title("채팅 UI")

# ── 대화 기록 초기화 (최초 1회) ──────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []

# ── 기존 대화 내용 화면에 출력 ───────────────────────────────────────────────

# session_state에 저장된 메시지를 순서대로 화면에 그립니다.
# Streamlit은 코드를 위에서 아래로 다시 실행하기 때문에
# 이 과정이 없으면 이전 대화가 사라집니다.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):  # "user" or "assistant"
        st.write(message["content"])

# ── 새 메시지 입력 ────────────────────────────────────────────────────────────

user_input = st.chat_input("메시지를 입력하세요")

if user_input:
    # 1. 사용자 메시지를 화면에 표시
    with st.chat_message("user"):
        st.write(user_input)

    # 2. 사용자 메시지를 기록에 저장
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 3. AI 응답 생성 (여기에 실제 agent.invoke()를 연결하면 됩니다!)
    response = f"'{user_input}'라고 하셨군요! (에이전트 응답이 여기에 들어옵니다)"

    # 4. AI 응답을 화면에 표시
    with st.chat_message("assistant"):
        st.write(response)

    # 5. AI 응답을 기록에 저장
    st.session_state.messages.append({"role": "assistant", "content": response})
