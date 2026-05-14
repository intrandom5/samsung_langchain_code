"""
Step 7: 완성형 챗봇 — 도구 호출 시각화
========================================
Step 1~6에서 배운 모든 것을 통합한 완성형 챗봇 앱입니다.

추가된 기능:
    - 도구 호출 과정을 사용자에게 상세하게 시각화
    - 대화 기록에 도구 실행 정보도 함께 저장/표시
    - 에러 처리

실행 방법:
    streamlit run step7_complete.py

📌 Step 6 대비 추가 사항:
    - 도구 이름과 결과를 st.expander()로 펼쳐서 볼 수 있게 표시
    - 대화 기록 저장 시 도구 실행 결과도 포함
    - 전반적인 UX 완성도 향상
"""
import os
import uuid
import base64

import streamlit as st
from dotenv import load_dotenv, find_dotenv
from langchain_core.messages import AIMessageChunk, ToolMessage

load_dotenv(find_dotenv())

st.set_page_config(
    page_title="AI 챗봇 (완성형)",
    page_icon="🚀",
    layout="wide",
)

# ═══════════════════════════════════════════════════════════════════════════════
# 에이전트 초기화
# ═══════════════════════════════════════════════════════════════════════════════
@st.cache_resource
def load_agent():
    from langchain_openai import ChatOpenAI
    from langchain.agents import create_agent
    from langgraph.checkpoint.memory import InMemorySaver
    from langchain.tools import tool

    @tool
    def get_weather(city: str) -> str:
        """도시 이름을 받아서 현재 날씨와 옷차림 추천 정보를 반환합니다."""
        weather_db = {
            "서울": ("맑음", 23, 55, "가벼운 겉옷을 챙기세요."),
            "부산": ("흐림", 20, 70, "우산을 준비하는 게 좋겠어요."),
            "제주": ("비", 18, 85, "우비나 우산이 꼭 필요합니다."),
            "대전": ("맑음", 25, 50, "반팔이면 충분해요!"),
            "인천": ("구름많음", 21, 65, "얇은 겉옷을 챙기세요."),
        }
        if city in weather_db:
            sky, temp, hum, tip = weather_db[city]
            return f"[{city}] {sky}, 기온 {temp}°C, 습도 {hum}% — {tip}"
        return f"'{city}'의 날씨 정보를 찾을 수 없습니다. (지원 도시: 서울, 부산, 제주, 대전, 인천)"

    @tool
    def calculate(expression: str) -> str:
        """
        수식 문자열을 계산합니다.
        지원: +, -, *, /, **, //, % 및 괄호
        예시: '2 + 3 * 4', '(100 - 20) / 4', '2 ** 10'
        """
        try:
            # 안전하지 않은 문자 필터링 (기본적인 보호)
            allowed = set("0123456789+-*/.() ")
            if not all(c in allowed for c in expression):
                return "허용되지 않는 문자가 포함되어 있습니다."
            result = eval(expression)  # noqa: S307
            return f"{expression} = {result}"
        except ZeroDivisionError:
            return "0으로 나눌 수 없습니다."
        except Exception as e:
            return f"계산 오류: {e}"

    @tool
    def translate(text: str, target_language: str = "영어") -> str:
        """
        텍스트를 지정한 언어로 번역합니다.
        target_language 예시: "영어", "일본어", "중국어", "스페인어"
        (실제 번역 API 대신 데모용으로 간단히 구현)
        """
        # 실제 서비스라면 번역 API를 호출하겠지만, 여기서는 데모용 응답만 반환
        return f"'{text}' → [{target_language} 번역 기능은 데모에서 지원하지 않습니다. 실제 API 연동이 필요합니다]"

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

    return create_agent(
        llm,
        tools=[get_weather, calculate, translate],
        system_prompt=(
            "당신은 친절하고 유능한 한국어 AI 어시스턴트입니다.\n"
            "사용 가능한 도구: 날씨 조회(get_weather), 계산(calculate), 번역(translate)\n"
            "도구가 필요하면 사용하고, 결과를 자연스러운 한국어로 설명해주세요.\n"
            "답변은 간결하되 친절하게 해주세요."
        ),
        checkpointer=InMemorySaver(),
    )

# ═══════════════════════════════════════════════════════════════════════════════
# 헬퍼 함수
# ═══════════════════════════════════════════════════════════════════════════════
def render_message(msg: dict):
    """저장된 메시지 딕셔너리를 화면에 표시합니다."""
    with st.chat_message(msg["role"]):
        # 도구 실행 정보가 있으면 먼저 표시
        for tool_result in msg.get("tool_results", []):
            with st.expander(f"🔧 {tool_result['name']} 도구 실행 결과", expanded=False):
                st.code(tool_result["result"], language=None)

        st.markdown(msg["content"])

# ═══════════════════════════════════════════════════════════════════════════════
# 페이지 레이아웃
# ═══════════════════════════════════════════════════════════════════════════════
st.title("🚀 AI 챗봇 — 완성형")
st.caption("도구 호출 시각화 + 스트리밍 응답 + 대화 기록 유지")

# ── 사이드바 ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ 설정")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())

    if st.button("🗑️ 대화 초기화", use_container_width=True):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()

    st.divider()

    # 대화 통계
    total = len(st.session_state.messages)
    user_count = sum(1 for m in st.session_state.messages if m["role"] == "user")
    col1, col2 = st.columns(2)
    col1.metric("총 메시지", total)
    col2.metric("내 메시지", user_count)

    st.divider()

    st.markdown("**🔧 사용 가능한 도구**")
    st.markdown("""
    - 🌤️ **날씨 조회** — 5개 도시 지원
    - 🧮 **계산기** — 사칙연산, 거듭제곱
    - 🌐 **번역** — (데모)
    """)

    st.divider()

    st.markdown("**💬 질문 예시**")
    st.markdown("""
    - 서울이랑 제주 날씨 비교해줘
    - 1234 * 5678 계산해줘
    - (100 - 37) / 3은 얼마야?
    - 부산 날씨 어때? 오늘 뭐 입을지 추천해줘
    - 안녕! 뭘 할 수 있어?
    """)

    st.divider()
    st.caption(f"session: `{st.session_state.thread_id[:8]}...`")

# ═══════════════════════════════════════════════════════════════════════════════
# 대화 내용 표시
# ═══════════════════════════════════════════════════════════════════════════════
# 처음 접속 시 인사말 표시
if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown(
            "안녕하세요! 저는 날씨 조회, 계산, 번역 도구를 사용할 수 있는 AI 어시스턴트입니다. 😊\n\n"
            "왼쪽 사이드바에서 질문 예시를 참고해서 말을 걸어보세요!"
        )

# 저장된 대화 기록 표시 (도구 실행 결과 포함)
for msg in st.session_state.messages:
    render_message(msg)

# ═══════════════════════════════════════════════════════════════════════════════
# 새 메시지 처리
# ═══════════════════════════════════════════════════════════════════════════════
if prompt := st.chat_input("메시지를 입력하세요..."):

    # ── 1. 사용자 메시지 ───────────────────────────────────────────────────────
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # ── 2. AI 응답 스트리밍 ────────────────────────────────────────────────────
    with st.chat_message("assistant"):
        response_placeholder = st.empty()   # 텍스트 응답을 갱신할 자리
        tool_status = st.empty()            # 도구 호출 중 상태 표시 자리

        full_response = ""
        # 이번 응답에서 실행된 도구들의 결과를 수집합니다
        # (대화 기록에 저장해두면 나중에 다시 표시할 수 있음)
        tool_results = []
        current_tool_name = None  # 현재 호출 중인 도구 이름 추적

        try:
            for chunk, _metadata in load_agent().stream(
                {"messages": {"role": "user", "content": prompt}},
                {"configurable": {"thread_id": st.session_state.thread_id}},
                stream_mode="messages",
            ):

                if isinstance(chunk, AIMessageChunk):

                    # 도구 호출 청크: AI가 어떤 도구를 쓸지 결정하는 중
                    if getattr(chunk, "tool_call_chunks", None):
                        for tc in chunk.tool_call_chunks:
                            if tc.get("name"):
                                current_tool_name = tc["name"]
                                tool_status.info(f"🔧 **{current_tool_name}** 도구를 호출하는 중...")

                    # 일반 텍스트 청크: AI의 실제 답변
                    if chunk.content:
                        full_response += chunk.content
                        response_placeholder.markdown(full_response + "▌")

                elif isinstance(chunk, ToolMessage):
                    # 도구 실행 완료!
                    tool_name = current_tool_name or "도구"
                    tool_result_text = chunk.content

                    # 도구 결과를 수집 (나중에 expander로 표시 + 기록 저장)
                    tool_results.append({
                        "name": tool_name,
                        "result": tool_result_text,
                    })

                    # 도구 결과를 expander로 즉시 표시 (스트리밍 중에도 표시 가능)
                    with st.expander(f"🔧 {tool_name} 실행 결과", expanded=False):
                        st.code(tool_result_text, language=None)

                    tool_status.empty()  # "실행 중..." 표시 제거
                    current_tool_name = None

        except Exception as e:
            full_response = f"죄송합니다. 오류가 발생했습니다: {e}"
            st.error(full_response)

        # 스트리밍 완료 정리
        tool_status.empty()
        response_placeholder.markdown(full_response)

    # ── 3. 응답 저장 (도구 결과 포함) ─────────────────────────────────────────
    # tool_results도 함께 저장해두면, 나중에 render_message()가 expander로 다시 표시함
    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response,
        "tool_results": tool_results,  # 도구 실행 기록
    })
