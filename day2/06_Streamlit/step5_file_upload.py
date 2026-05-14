# 실행 방법:
# day2/06_Streamlit 폴더로 이동
# conda activate llm-agent
# streamlit run step5_agent_chat.py
#
# [이번 단계에서 배울 것]
# 파일을 업로드해서 LLM과 대화하는 앱을 만듭니다.
# 파일 내용을 session_state에 저장해야 하는 이유를 이해합니다.
#
# ─────────────────────────────────────────────────────────────────────────────
# 파일 업로드에서 session_state가 필요한 이유
# ─────────────────────────────────────────────────────────────────────────────
#
# st.file_uploader 는 사용자가 파일을 올려두더라도,
# 코드가 재실행되면 위젯이 다시 그려지면서 파일 객체가 사라질 수 있습니다.
#
# 예를 들어 파일을 올리고 채팅 메시지를 보내면:
#   1. 채팅 입력 → 재실행 발생
#   2. file_uploader 위젯 재생성 → 파일 객체 None으로 초기화
#   3. 파일에서 뽑은 텍스트가 사라져 LLM에 전달 불가
#
# 해결책: 파일에서 텍스트를 추출한 즉시 session_state에 저장합니다.
# 이후 재실행에서는 위젯 상태와 무관하게 session_state에서 읽어 씁니다.

import os
import io
import uuid
import streamlit as st
from dotenv import load_dotenv, find_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

load_dotenv(find_dotenv())


# ── LLM 클라이언트 (앱 전체에서 1회만 생성) ──────────────────────────────────

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


# ── 파일에서 텍스트 추출 ──────────────────────────────────────────────────────

def extract_text(uploaded_file) -> str:
    name = uploaded_file.name.lower()

    if name.endswith(".txt"):
        return uploaded_file.read().decode("utf-8", errors="ignore")

    if name.endswith(".pdf"):
        import PyPDF2
        reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    if name.endswith(".docx"):
        import docx
        doc = docx.Document(io.BytesIO(uploaded_file.read()))
        return "\n".join(p.text for p in doc.paragraphs)

    return ""


# ── UI ────────────────────────────────────────────────────────────────────────

st.title("파일 첨부 채팅")

# ── session_state 초기화 (최초 1회) ──────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []

if "file_text" not in st.session_state:
    # 업로드된 파일의 텍스트를 저장하는 공간
    # 파일을 올리는 순간 추출해서 여기 저장하고, 이후 재실행에서도 유지합니다.
    st.session_state.file_text = None

if "file_name" not in st.session_state:
    st.session_state.file_name = None

# ── 사이드바: 파일 업로드 ─────────────────────────────────────────────────────

with st.sidebar:
    st.subheader("파일 첨부")

    uploaded_file = st.file_uploader(
        "파일을 업로드하세요",
        type=["txt", "pdf", "docx"],
        # key를 고정하지 않으면 재실행마다 위젯 ID가 바뀌어 파일이 날아갈 수 있습니다.
        key="file_uploader",
    )

    # 새 파일이 올라왔을 때만 텍스트 추출 후 session_state에 저장
    if uploaded_file is not None and uploaded_file.name != st.session_state.file_name:
        with st.spinner("파일 읽는 중..."):
            text = extract_text(uploaded_file)
        if text.strip():
            st.session_state.file_text = text
            st.session_state.file_name = uploaded_file.name
            st.success(f"'{uploaded_file.name}' 로드 완료 ({len(text):,}자)")
        else:
            st.warning("텍스트를 추출할 수 없는 파일입니다.")

    # 파일이 제거되면 session_state도 함께 초기화
    if uploaded_file is None and st.session_state.file_name is not None:
        st.session_state.file_text = None
        st.session_state.file_name = None

    # 현재 로드된 파일 표시
    if st.session_state.file_name:
        st.info(f"현재 파일: {st.session_state.file_name}")
        with st.expander("파일 내용 미리보기"):
            st.text(st.session_state.file_text[:1000] + "...")

    st.divider()

    if st.button("대화 초기화"):
        st.session_state.messages = []
        st.rerun()

# ── 이전 대화 출력 ────────────────────────────────────────────────────────────

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ── 새 메시지 입력 및 LLM 호출 ───────────────────────────────────────────────

file_loaded = st.session_state.file_text is not None
placeholder = "파일에 대해 질문하세요" if file_loaded else "메시지를 입력하세요 (파일 없이도 대화 가능)"

if user_input := st.chat_input(placeholder):

    # 1. 사용자 메시지 표시 & 저장
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 2. 시스템 프롬프트 구성
    #    파일이 있으면 내용을 시스템 프롬프트에 삽입합니다.
    #    session_state.file_text 덕분에 재실행 후에도 파일 내용을 참조할 수 있습니다.
    if st.session_state.file_text:
        system_content = (
            "당신은 친절한 AI 어시스턴트입니다. 한국어로 답변하세요.\n\n"
            "아래는 사용자가 첨부한 파일의 내용입니다. 질문에 답할 때 이 내용을 참고하세요.\n\n"
            f"[파일명: {st.session_state.file_name}]\n"
            f"{st.session_state.file_text[:8000]}"  # 토큰 한도를 고려해 앞부분만 전달
        )
    else:
        system_content = "당신은 친절한 AI 어시스턴트입니다. 한국어로 답변하세요."

    # 3. 전체 대화 기록 → LangChain 메시지 형식으로 변환
    langchain_messages = [SystemMessage(content=system_content)]
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            langchain_messages.append(HumanMessage(content=msg["content"]))
        else:
            langchain_messages.append(AIMessage(content=msg["content"]))

    # 4. LLM 호출
    with st.chat_message("assistant"):
        with st.spinner("생각 중..."):
            llm = get_llm()
            response = llm.invoke(langchain_messages)
            answer = response.content
        st.write(answer)

    # 5. AI 응답 저장
    st.session_state.messages.append({"role": "assistant", "content": answer})
