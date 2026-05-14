# 실행 방법:
# 07_kiki_agent_ui 폴더로 이동
# conda activate llm-agent
# streamlit run app.py

import os
import sys
import uuid
import shutil
import pandas as pd
import streamlit as st
from pathlib import Path

# kiki_agent를 패키지로 인식시키기 위해 현재 폴더를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv, find_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver

# kiki_agent 폴더는 건드리지 않고 rag_retriever만 import
from kiki_agent.agent.rag_retriever import RAGRetriever

load_dotenv(find_dotenv())

# ── 경로 설정 ─────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).parent
DOCS_DIR = BASE_DIR / "registered_docs"
AGENTS_MD = BASE_DIR / "kiki_agent" / "agent" / "agents.md"

# 카테고리별 폴더 생성
for cat in ("product", "policy", "employee"):
    (DOCS_DIR / cat).mkdir(parents=True, exist_ok=True)

CATEGORY_KO = {
    "product":  "제품/회사 소개",
    "policy":   "사내 규정",
    "employee": "임직원 정보",
}
ALLOWED_EXT = {
    "product":  [".pdf", ".pptx"],
    "policy":   [".docx"],
    "employee": [".xlsx"],
}


# ── LLM (앱 전체에서 1회 생성) ────────────────────────────────────────────────

@st.cache_resource
def get_llm():
    return ChatOpenAI(
        model=os.getenv("model"),
        base_url=os.getenv("api_base_url"),
        default_headers={
            "x-dep-ticket":     os.getenv("credential_key"),
            "Send-System-Name": os.getenv("send_system_name"),
            "User-Id":          os.getenv("user_id"),
            "User-Type":        "AD_ID",
            "Prompt-Msg-Id":    str(uuid.uuid4()),
            "Completion-Msg-Id": str(uuid.uuid4()),
        },
        temperature=0.7,
    )


# ── 에이전트 빌드 ─────────────────────────────────────────────────────────────
#
# tools.py의 RAG_DIR 미정의 버그 때문에 kiki_agent.agent.agent를 직접 import하면
# NameError가 발생합니다. 대신 rag_retriever.py만 import해서 여기서 직접 빌드합니다.
#
# 에이전트는 빌드 비용(임베딩 API 호출)이 크므로 session_state에 저장해 재사용합니다.

def build_agent():
    llm = get_llm()
    supervisor_tools = []

    # ── 제품/회사 소개 RAG ────────────────────────────────────────────────────
    product_files = list((DOCS_DIR / "product").iterdir())
    if product_files:
        product_rag = RAGRetriever()
        for f in product_files:
            product_rag.add_file(str(f))
        product_rag.build_retriever()

        product_sub = create_agent(
            llm,
            tools=[_make_product_tool(product_rag)],
            system_prompt="당신은 키키테크 제품 전문 에이전트입니다. search_product 도구로 제품 정보를 찾아 답변하세요.",
        )

        @tool
        def ask_product_agent(query: str) -> str:
            """키키테크 제품 소개, 기능, 가격, 회사 개요 등 제품과 회사 관련 질문을 처리합니다."""
            result = product_sub.invoke({"messages": [{"role": "user", "content": query}]})
            return result["messages"][-1].content

        supervisor_tools.append(ask_product_agent)

    # ── 사내 규정 RAG ─────────────────────────────────────────────────────────
    policy_files = list((DOCS_DIR / "policy").iterdir())
    if policy_files:
        policy_rag = RAGRetriever()
        for f in policy_files:
            policy_rag.add_file(str(f))
        policy_rag.build_retriever()

        policy_sub = create_agent(
            llm,
            tools=[_make_policy_tool(policy_rag)],
            system_prompt="당신은 키키테크 사내 규정 전문 에이전트입니다. search_policy 도구로 규정을 찾아 답변하세요.",
        )

        @tool
        def ask_policy_agent(query: str) -> str:
            """근무 규정, 복리후생, 행동강령, 보안 정책 등 사내 규정 관련 질문을 처리합니다."""
            result = policy_sub.invoke({"messages": [{"role": "user", "content": query}]})
            return result["messages"][-1].content

        supervisor_tools.append(ask_policy_agent)

    # ── 임직원 정보 (Excel) ───────────────────────────────────────────────────
    employee_files = list((DOCS_DIR / "employee").iterdir())
    if employee_files:
        employee_path = str(employee_files[0])

        employee_sub = create_agent(
            llm,
            tools=[_make_employee_tool(employee_path)],
            system_prompt="당신은 키키테크 임직원 정보 전문 에이전트입니다. 임직원의 이름을 파악해서 search_employee 도구로 정보를 찾아 답변하세요.",
        )

        @tool
        def ask_employee_agent(query: str) -> str:
            """임직원 이름, 연락처, 부서, 담당업무, 프로젝트 현황 등 직원 관련 질문을 처리합니다."""
            result = employee_sub.invoke({"messages": [{"role": "user", "content": query}]})
            return result["messages"][-1].content

        supervisor_tools.append(ask_employee_agent)

    if not supervisor_tools:
        return None

    with open(AGENTS_MD, encoding="utf-8") as f:
        system_prompt = f.read()

    return create_agent(
        llm,
        tools=supervisor_tools,
        system_prompt=system_prompt,
        checkpointer=InMemorySaver(),  # 대화 상태를 내부에서 thread_id로 관리
    )


# @tool 데코레이터는 모듈 수준에서만 안정적으로 사용 가능하므로,
# 클로저가 필요한 경우에는 별도 헬퍼 함수로 분리합니다.

def _make_product_tool(rag: RAGRetriever):
    @tool
    def search_product(query: str) -> str:
        """키키테크 제품 정보와 회사 소개를 검색합니다."""
        return "\n\n---\n\n".join(doc.page_content for doc in rag.search(query))
    return search_product


def _make_policy_tool(rag: RAGRetriever):
    @tool
    def search_policy(query: str) -> str:
        """키키테크 사내 규정과 행동강령을 검색합니다."""
        return "\n\n---\n\n".join(doc.page_content for doc in rag.search(query))
    return search_policy


def _make_employee_tool(excel_path: str):
    @tool
    def search_employee(name: str) -> str:
        """임직원 이름으로 정보를 검색합니다. 연락처, 부서, 담당업무 등을 확인할 수 있습니다."""
        df = pd.read_excel(excel_path, header=1)
        result = df[df["성명"] == name]
        if result.empty:
            return f"'{name}' 이름의 임직원을 찾을 수 없습니다."
        row = result.iloc[0]
        return "\n".join(f"{col}: {row[col]}" for col in df.columns)
    return search_employee


# ── session_state 초기화 ──────────────────────────────────────────────────────

def init_state():
    if "agent" not in st.session_state:
        st.session_state.agent = None          # 빌드된 에이전트 (None이면 미빌드)
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())  # 세션별 대화 스레드 ID
    if "messages" not in st.session_state:
        st.session_state.messages = []         # 화면 표시용 대화 기록


# ── 페이지: 문서 관리 ─────────────────────────────────────────────────────────

def page_docs():
    st.title("📁 문서 관리")
    st.caption("문서를 업로드한 뒤 'RAG 빌드'를 누르면 에이전트가 문서를 학습합니다.")

    # ── 파일 업로드 ───────────────────────────────────────────────────────────
    st.subheader("파일 업로드")

    col_cat, col_up = st.columns([1, 2])
    with col_cat:
        selected_cat = st.selectbox(
            "카테고리",
            options=list(CATEGORY_KO.keys()),
            format_func=lambda k: CATEGORY_KO[k],
        )
    with col_up:
        exts = ALLOWED_EXT[selected_cat]
        uploaded = st.file_uploader(
            f"파일 선택 ({', '.join(exts)})",
            type=[e.lstrip(".") for e in exts],
            key="uploader",
        )

    if uploaded:
        dest = DOCS_DIR / selected_cat / uploaded.name
        dest.write_bytes(uploaded.read())
        st.success(f"'{uploaded.name}' 을(를) [{CATEGORY_KO[selected_cat]}]에 저장했습니다.")
        # 파일이 바뀌었으므로 기존 에이전트를 초기화 (재빌드 유도)
        st.session_state.agent = None

    st.divider()

    # ── 등록된 파일 목록 ──────────────────────────────────────────────────────
    st.subheader("등록된 문서")

    any_file = False
    for cat, label in CATEGORY_KO.items():
        files = sorted((DOCS_DIR / cat).iterdir())
        if not files:
            continue
        any_file = True
        st.markdown(f"**{label}**")
        for f in files:
            c1, c2 = st.columns([5, 1])
            c1.write(f"- {f.name}")
            if c2.button("삭제", key=f"del_{f}"):
                f.unlink()
                st.session_state.agent = None  # 문서 변경 → 재빌드 필요
                st.rerun()

    if not any_file:
        st.info("아직 등록된 문서가 없습니다. 위에서 파일을 업로드하세요.")

    st.divider()

    # ── RAG 빌드 ──────────────────────────────────────────────────────────────
    st.subheader("에이전트 빌드")

    if st.session_state.agent is None:
        st.warning("문서를 업로드한 후 빌드 버튼을 눌러 에이전트를 활성화하세요.")
    else:
        st.success("에이전트가 준비되었습니다. '채팅' 탭에서 대화를 시작하세요.")

    if st.button("🔨 RAG 빌드 시작", disabled=not any_file):
        with st.spinner("문서를 임베딩하고 에이전트를 빌드하는 중입니다... (수 분 소요)"):
            agent = build_agent()

        if agent:
            st.session_state.agent = agent
            st.session_state.messages = []          # 새 문서 → 대화 기록 초기화
            st.session_state.thread_id = str(uuid.uuid4())
            st.success("빌드 완료! '채팅' 탭으로 이동하세요.")
        else:
            st.error("빌드 실패: 등록된 문서가 없습니다.")


# ── 페이지: 채팅 ──────────────────────────────────────────────────────────────

def page_chat():
    st.title("💬 키키테크 Q&A 챗봇")

    # 에이전트 미준비 시 안내
    if st.session_state.agent is None:
        st.warning("아직 에이전트가 빌드되지 않았습니다. '문서 관리' 탭에서 빌드를 먼저 완료해 주세요.")
        return

    st.caption("예시 질문: '이서연 책임의 내선번호가 뭐야?' / '재택근무는 일주일에 몇 번까지 가능해?'")

    # 사이드바: 대화 초기화
    with st.sidebar:
        st.divider()
        if st.button("🔄 대화 초기화"):
            st.session_state.messages = []
            st.session_state.thread_id = str(uuid.uuid4())
            st.rerun()

    # ── 이전 대화 출력 ────────────────────────────────────────────────────────
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # ── 새 메시지 입력 ────────────────────────────────────────────────────────
    if user_input := st.chat_input("메시지를 입력하세요"):

        with st.chat_message("user"):
            st.write(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        # 에이전트 호출
        # InMemorySaver가 thread_id 기준으로 대화 상태를 내부 관리하므로
        # 여기서는 현재 입력만 전달해도 이전 문맥을 자동으로 이어받습니다.
        with st.chat_message("assistant"):
            with st.spinner("에이전트가 검색 중입니다..."):
                response = st.session_state.agent.invoke(
                    {"messages": [{"role": "user", "content": user_input}]},
                    {"configurable": {"thread_id": st.session_state.thread_id}},
                )
                answer = response["messages"][-1].content
            st.write(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})


# ── 앱 진입점 ─────────────────────────────────────────────────────────────────

st.set_page_config(page_title="키키테크 Q&A", page_icon="🤖", layout="wide")

init_state()

with st.sidebar:
    st.title("키키테크 Q&A")
    agent_status = "✅ 준비됨" if st.session_state.agent else "⚙️ 미빌드"
    st.caption(f"에이전트 상태: {agent_status}")
    page = st.radio("메뉴", ["📁 문서 관리", "💬 채팅"])

if page == "📁 문서 관리":
    page_docs()
else:
    page_chat()
