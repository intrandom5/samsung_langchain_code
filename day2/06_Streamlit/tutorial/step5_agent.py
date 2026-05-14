"""
Step 5: 에이전트 연동 기초
===========================
Step 4의 채팅 UI에 실제 LLM 에이전트를 연결합니다.
스트리밍 없이 invoke()로 완성된 응답을 한 번에 받습니다.

실행 방법:
    streamlit run step5_agent.py

📌 이번 단계에서 배우는 것:
    - @st.cache_resource : 에이전트를 앱 시작 시 딱 한 번만 초기화
    - agent.invoke()     : 에이전트에 메시지를 보내고 응답을 받음 (동기)
    - st.spinner()       : "생각 중..." 로딩 표시
    - thread_id          : 대화 세션을 구분하는 고유 ID

⚠️ 사전 준비:
    프로젝트 루트의 .env 파일에 아래 내용이 있어야 합니다:
        credential_key=your-api-key
        model=gpt-4o-mini
"""
import os
import uuid

import streamlit as st
from dotenv import load_dotenv, find_dotenv

# .env 파일에서 API 키 등 환경변수를 로드합니다
# find_dotenv()는 현재 폴더부터 상위로 올라가며 .env 파일을 찾습니다
load_dotenv(find_dotenv())

st.set_page_config(page_title="Step 5: 에이전트 연동", page_icon="🤖", layout="wide")
st.title("🤖 에이전트 연동 기초")

# ═══════════════════════════════════════════════════════════════════════════════
# @st.cache_resource 로 에이전트 초기화
# ═══════════════════════════════════════════════════════════════════════════════
# @st.cache_resource : 이 함수의 반환값을 앱 전체에서 한 번만 계산하고 캐시합니다.
#
# 왜 필요한가?
#   Streamlit은 사용자 조작마다 스크립트 전체를 다시 실행합니다.
#   에이전트 초기화에는 API 호출이나 모델 로딩이 필요할 수 있는데,
#   이걸 리런마다 반복하면 느리고 비용이 낭비됩니다.
#   @st.cache_resource는 "이 함수는 딱 한 번만 실행하고 결과를 재사용해"라는 의미입니다.
@st.cache_resource
def load_agent():
    """
    에이전트를 초기화하고 반환합니다.
    앱이 처음 실행될 때 한 번만 호출되며, 이후에는 캐시된 결과를 사용합니다.
    """
    from langchain_openai import ChatOpenAI
    from langchain.agents import create_agent
    from langgraph.checkpoint.memory import InMemorySaver
    from langchain.tools import tool

    # ── 도구 정의 ────────────────────────────────────────────────────────────
    # @tool 데코레이터: 함수를 에이전트가 사용할 수 있는 도구로 만듭니다
    # 독스트링(docstring)이 에이전트에게 "이 도구가 무엇을 하는지" 설명합니다

    @tool
    def get_weather(city: str) -> str:
        """도시 이름을 받아서 현재 날씨 정보를 반환합니다."""
        # 실제로는 날씨 API를 호출하지만, 여기서는 간단하게 하드코딩합니다
        weather_db = {
            "서울": "맑음, 기온 23°C, 습도 55%",
            "부산": "흐림, 기온 20°C, 습도 70%",
            "제주": "비, 기온 18°C, 습도 85%",
            "대전": "맑음, 기온 25°C, 습도 50%",
        }
        return weather_db.get(city, f"'{city}'의 날씨 정보를 찾을 수 없습니다. (서울, 부산, 제주, 대전만 지원)")

    @tool
    def calculate(expression: str) -> str:
        """수식 문자열을 계산합니다. 예: '2 + 3 * 4', '100 / 5'"""
        try:
            # eval()은 보안상 위험할 수 있으나, 여기서는 학습 목적으로 사용합니다
            result = eval(expression)  # noqa: S307
            return f"{expression} = {result}"
        except Exception as e:
            return f"계산 오류: {e}"

    # ── 모델 초기화 ───────────────────────────────────────────────────────────
    os.environ["OPENAI_API_KEY"] = 'api_key'
    llm = ChatOpenAI(
        model=os.getenv("model"),
        base_url=os.getenv("api_base_url"),
        default_headers={
            'x-dep-ticket': os.getenv("credential_key"),
            'Send-System-Name': os.getenv("send_system_name"),
            'User-Id': os.getenv("user_id"),
            'User-Type': "AD_ID",
            'Prompt-Msg-Id': str(uuid.uuid4()),
            'Completion-Msg-Id': str(uuid.uuid4())
        },
        temperature=0.7,
    )

    # ── 에이전트 생성 ─────────────────────────────────────────────────────────
    return create_agent(
        llm,
        tools=[get_weather, calculate],   # 사용 가능한 도구 목록
        system_prompt=(
            "당신은 친절한 한국어 AI 어시스턴트입니다. "
            "날씨 조회와 계산 도구를 사용할 수 있습니다. "
            "질문에 간결하고 정확하게 답변하세요."
        ),
        # InMemorySaver: 대화 기록을 서버 메모리에 저장합니다.
        # thread_id로 여러 대화 세션을 구분합니다.
        checkpointer=InMemorySaver(),
    )

# ═══════════════════════════════════════════════════════════════════════════════
# Session State 초기화
# ═══════════════════════════════════════════════════════════════════════════════
if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    # uuid4()로 무작위 고유 ID를 생성합니다.
    # 에이전트는 이 ID로 "이 대화는 어떤 사용자와의 것인지" 구분하고
    # 대화 맥락(context)을 유지합니다.
    st.session_state.thread_id = str(uuid.uuid4())

# ── 사이드바 ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ 설정")

    if st.button("🗑️ 대화 초기화", use_container_width=True):
        st.session_state.messages = []
        # 새 대화를 시작할 때 thread_id도 갱신합니다.
        # 기존 thread_id를 유지하면 에이전트가 이전 대화를 기억합니다.
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()

    st.divider()

    # thread_id 표시 (앞 8자리만)
    st.caption("현재 대화 세션:")
    st.code(st.session_state.thread_id[:8] + "...", language=None)

    st.divider()

    st.markdown("**사용 가능한 도구**")
    st.markdown("""
    - 🌤️ **날씨 조회**: "서울 날씨 알려줘"
    - 🧮 **계산**: "123 * 456 계산해줘"
    """)

    st.divider()

    st.markdown("**질문 예시**")
    st.markdown("""
    - 안녕! 자기소개 해줘
    - 서울이랑 부산 날씨 비교해줘
    - (2 + 3) * 10 계산해줘
    - 오늘 제주도 날씨 어때?
    """)

# ═══════════════════════════════════════════════════════════════════════════════
# 기존 대화 표시
# ═══════════════════════════════════════════════════════════════════════════════
# 대화가 없으면 안내 메시지 표시
if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown("안녕하세요! 날씨 조회와 계산 도구를 사용할 수 있어요. 무엇이든 물어보세요! 😊")

# 저장된 대화 기록을 순서대로 화면에 표시
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ═══════════════════════════════════════════════════════════════════════════════
# 새 메시지 처리
# ═══════════════════════════════════════════════════════════════════════════════
if prompt := st.chat_input("메시지를 입력하세요..."):

    # 1. 사용자 메시지 표시 및 저장
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. AI 응답 생성 (invoke = 완성된 응답을 한 번에 받기)
    with st.chat_message("assistant"):

        # st.spinner() : 작업이 완료될 때까지 로딩 아이콘과 메시지를 표시합니다
        with st.spinner("생각 중..."):
            try:
                # agent.invoke() : 에이전트에 메시지를 보내고 최종 응답을 기다립니다.
                # configurable의 thread_id로 대화 맥락을 구분합니다.
                result = load_agent().invoke(
                    {"messages": {"role": "user", "content": prompt}},
                    {"configurable": {"thread_id": st.session_state.thread_id}},
                )
                # 에이전트 결과에서 마지막 메시지(최종 AI 답변)를 꺼냅니다
                response = result["messages"][-1].content

            except Exception as e:
                response = f"오류가 발생했습니다: {e}"
                st.error(response)

        st.markdown(response)

    # 3. AI 응답 저장
    st.session_state.messages.append({"role": "assistant", "content": response})

# ── 하단 안내 ─────────────────────────────────────────────────────────────────
st.divider()
st.info("""
**Step 5 vs Step 6의 차이점**

Step 5에서는 `agent.invoke()`를 사용합니다.
이 방식은 에이전트가 생각을 완료할 때까지 기다린 후, 완성된 응답을 한 번에 화면에 표시합니다.
도구를 여러 번 호출하거나 긴 답변일 경우 **사용자가 기다리는 시간이 느껴질 수 있습니다**.

Step 6에서는 `agent.stream()`으로 토큰이 생성되는 즉시 화면에 표시해서
**ChatGPT처럼 글자가 하나씩 나타나는 효과**를 구현합니다.
""")
