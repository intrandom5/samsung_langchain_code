# 실행 방법:
# day2/06_Streamlit 폴더로 이동
# conda activate llm-agent
# streamlit run step6_agent_chat.py
#
# [이번 단계에서 배울 것]
# 실제 LLM과 연결된 채팅 앱을 만들면서
# session_state가 두 가지 역할을 동시에 한다는 것을 이해합니다.
#
# ─────────────────────────────────────────────────────────────────────────────
# session_state가 필요한 이유 (대화 앱 버전)
# ─────────────────────────────────────────────────────────────────────────────
#
# [역할 1] 화면 재구성
#   Streamlit은 메시지를 보낼 때마다 코드를 처음부터 다시 실행합니다.
#   이전 채팅 버블을 다시 그리려면 기록을 어딘가에 보관해야 합니다.
#   → session_state.messages 에 저장
#
# [역할 2] LLM 문맥 유지
#   LLM은 상태가 없습니다(stateless). API를 호출할 때마다 빈 상태로 시작합니다.
#   "아까 내가 말한 거 기억해?"가 되려면, 이전 대화를 매번 같이 전달해야 합니다.
#   → session_state.messages 를 LangChain 메시지 형식으로 변환해서 LLM에 전달
#
# 결국 하나의 messages 리스트가 UI 재구성과 LLM 문맥 유지를 모두 담당합니다.

import os
import uuid
import streamlit as st
from dotenv import load_dotenv, find_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

load_dotenv(find_dotenv())

# ── LLM 클라이언트 생성 ───────────────────────────────────────────────────────
#
# @st.cache_resource 를 쓰는 이유:
#   - Streamlit은 재실행마다 모든 코드를 다시 실행합니다.
#   - cache_resource 없이는 메시지를 보낼 때마다 LLM 객체가 새로 만들어집니다.
#   - cache_resource 는 앱 전체 생애 동안 딱 한 번만 실행되어 객체를 재사용합니다.
#   - session_state 와의 차이: session_state는 사용자별 저장소,
#     cache_resource는 서버 전체 공유 캐시(모든 사용자가 같은 객체를 씁니다).

@st.cache_resource
def get_llm():
    return ChatOpenAI(
        model=os.getenv("model"),
        base_url=os.getenv("api_base_url"),
        default_headers={
            "x-dep-ticket": os.getenv("credential_key"),
            "Send-System-Name": os.getenv("send_system_name"),
            "User-Id": os.getenv("user_id"),
            "User-Type": "AD_ID",
            "Prompt-Msg-Id": str(uuid.uuid4()),
            "Completion-Msg-Id": str(uuid.uuid4()),
        },
        temperature=0.7,
    )


# ── UI ────────────────────────────────────────────────────────────────────────

st.title("LLM 에이전트 채팅")
st.caption("대화 내역이 session_state에 저장되어 문맥이 유지됩니다.")

# ── 대화 기록 초기화 (최초 1회) ──────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []  # {"role": "user"|"assistant", "content": "..."}

# ── 사이드바: 대화 기록 시각화 ───────────────────────────────────────────────

with st.sidebar:
    st.subheader("session_state 내부")
    st.caption("LLM에 전달되는 메시지 목록입니다.")
    st.json(st.session_state.messages)

    if st.button("대화 초기화"):
        st.session_state.messages = []
        st.rerun()

# ── 이전 대화 화면에 출력 ─────────────────────────────────────────────────────
#
# 재실행마다 이 루프가 session_state의 기록을 읽어 채팅 버블을 다시 그립니다.
# 이 코드가 없으면 새 메시지를 보낼 때 이전 대화가 모두 사라집니다.

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ── 새 메시지 입력 및 LLM 호출 ───────────────────────────────────────────────

if user_input := st.chat_input("메시지를 입력하세요"):

    # 1. 사용자 메시지를 화면에 표시하고 기록에 저장
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 2. session_state의 전체 대화 기록을 LangChain 메시지 형식으로 변환
    #
    #    LLM은 호출할 때마다 이전 내용을 기억하지 못합니다.
    #    그래서 "지금까지의 대화 전체"를 매번 LLM에 넘겨야 문맥이 유지됩니다.
    #    session_state에 저장해 뒀기 때문에 이 변환이 가능합니다.
    langchain_messages = [
        SystemMessage(content="당신은 친절한 AI 어시스턴트입니다. 한국어로 답변하세요.")
    ]
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            langchain_messages.append(HumanMessage(content=msg["content"]))
        else:
            langchain_messages.append(AIMessage(content=msg["content"]))

    # 3. LLM 호출 및 응답 표시
    with st.chat_message("assistant"):
        with st.spinner("생각 중..."):
            llm = get_llm()
            response = llm.invoke(langchain_messages)
            answer = response.content
        st.write(answer)

    # 4. AI 응답도 기록에 저장 (다음 재실행 때 화면 재구성 + LLM 문맥에 사용)
    st.session_state.messages.append({"role": "assistant", "content": answer})
