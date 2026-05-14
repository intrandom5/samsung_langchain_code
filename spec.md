# 삼성전자 CS Agent 프로젝트 명세서

> LangChain `create_agent` 기반 고객 문의 & 제품 불량 대응 멀티 에이전트 시스템

---

## 1. 문제 상황 정의

삼성전자 CS 센터에는 하루 수천 건의 고객 문의가 접수된다. 대부분은 배터리 설정, 와이파이 연결, 초기화 방법 같은 반복적인 질문이지만, 상담원이 방대한 제품 매뉴얼을 실시간으로 참조하며 답변하기 어렵다.

또한 물리적 손상, 환불 요청, 반복 미해결 케이스처럼 상담원이 직접 개입해야 하는 상황을 놓치는 경우도 발생한다.

| 문제 | 내용 |
|---|---|
| 반복 문의 과부하 | 동일한 질문이 하루 수천 건 반복 접수, 상담원 리소스 낭비 |
| 매뉴얼 파악 한계 | 신제품 출시마다 두꺼워지는 매뉴얼을 실시간 참조하기 어려움 |
| 불량 접수 지연 | 불량 유형 판단 → 교환/수리 결정까지 다단계 확인으로 처리 지연 |
| 에스컬레이션 누락 | 복잡한 케이스가 1차 상담에서 해결 안 되면 인계가 누락되는 경우 발생 |

---

## 2. LangChain 에이전트가 필요한 이유

단순 챗봇은 정해진 답변만 반환한다. 하지만 CS 현장은 문의 유형이 다양하고, 상황에 따라 다른 행동이 필요하다.

- 일반 문의면 → 문서 검색 후 답변 생성
- 해결 불가면 → 티켓 생성 후 상담원 인계
- 판단이 애매한 케이스면 → confidence 기반으로 안전하게 에스컬레이션

**상황을 판단하고 다음 행동을 스스로 결정하는 구조**가 필요하기 때문에 LangChain의 `create_agent`를 사용한다.

---

## 3. 에이전트 구조

### 3-1. 전체 흐름

```
고객 입력
  → [분류 Agent]        문의 유형 판단 (일반문의 / 불량신고)
  → [RAG 검색 Agent]    로컬 파일 기반 관련 문서 검색
  → [답변 생성 Agent]   검색 결과 기반 답변 생성 + 해결 가능 여부 판단
       ├── 해결됨   → 답변 반환
       └── 미해결   → [에스컬레이션 Agent]  티켓 생성 + 상담원 인계 메시지
```

Agent 4개가 각자 역할을 가지고, 오케스트레이터 함수가 순서와 분기를 제어한다.

### 3-2. Agent별 역할 정의

| Agent | 역할 | 사용 모델 | Tool |
|---|---|---|---|
| 분류 Agent | 문의를 일반문의 / 불량신고로 분류 | Samsung 사내 AI | `classify_query` |
| RAG 검색 Agent | 로컬 문서에서 관련 내용 검색 | Samsung 사내 AI | `search_docs` |
| 답변 생성 Agent | 검색 결과 기반 답변 생성, 해결 가능 여부 판단 | Samsung 사내 AI | `check_resolved` |
| 에스컬레이션 Agent | 미해결 케이스 티켓 생성 및 인계 메시지 작성 | Samsung 사내 AI | `create_ticket` |

> **Samsung 사내 AI는 단일 모델 하나만 사용한다.** `.env`에 설정된 모델명을 모든 Agent가 공유한다.

### 3-3. Structured Output 설계

Agent 간 데이터 전달 신뢰성을 확보하기 위해 모든 Agent 출력을 구조화한다.

```python
@dataclass
class ClassifyResult:
    category: str        # "일반문의" | "불량신고"
    confidence: float    # 0.0 ~ 1.0

@dataclass
class SearchResult:
    docs: list[str]      # 검색된 문서 청크 리스트
    found: bool          # 관련 문서 존재 여부

@dataclass
class AnswerResult:
    answer: str          # 생성된 답변
    should_escalate: bool
    confidence: float    # 0.0 ~ 1.0 (0.7 미만이면 자동 에스컬레이션)
    reason: str          # 에스컬레이션 사유

@dataclass
class TicketResult:
    ticket_id: str       # 티켓 번호
    message: str         # 고객에게 전달할 인계 메시지
```

### 3-4. 에스컬레이션 판단 기준

프롬프트 + few-shot + confidence 임계값 3중 구조로 설계한다.

**에스컬레이션 O**
- 물리적 손상이 언급된 경우 (화면 파손, 침수 등)
- 환불 / 교환 요청이 포함된 경우
- 동일 문제로 2회 이상 재문의한 경우
- 검색된 관련 문서가 없는 경우
- confidence < 0.7인 경우 (판단 불확실)

**에스컬레이션 X**
- FAQ 또는 매뉴얼에 단계별 해결책이 존재하는 경우
- 설정 변경, 초기화 등 소프트웨어적 해결이 가능한 경우

---

## 4. 프로젝트 진행 절차

### Step 1. RAG 데이터 준비

로컬 텍스트 파일로 지식 베이스를 구성한다. 실제 삼성 문서 없이 샘플 데이터로 대체한다.

**파일 구성**

```
data/
  galaxy_faq.txt        # 갤럭시 S25 자주 묻는 질문 20~30개
  product_manual.txt    # 기능 설명, 초기설정, 문제해결 가이드
  defect_history.txt    # 불량 유형별 처리 이력 예시 (수리/교환/환불)
  as_policy.txt         # 무상 보증 기간, 유상 수리 기준
```

**데이터 처리 방식**

- 파일 로딩 → 청킹 (chunk_size=500, overlap=50)
- 청크를 리스트로 메모리에 보관 (로컬 저장, 별도 DB 없음)
- 검색은 **BM25 키워드 매칭**으로 구현 (벡터 DB 불필요)

> **Embedding API는 사용하지 않는다.** Samsung 사내 API의 embedding endpoint 지원 여부가 불확실하므로, BM25 기반 키워드 검색으로 대체한다.

### Step 2. 툴 정의

각 Agent가 사용할 tool 함수를 `@tool` 데코레이터로 정의한다.

```python
from langchain.tools import tool

@tool
def classify_query(query: str) -> str:
    """고객 문의를 '일반문의' 또는 '불량신고'로 분류한다."""
    ...

@tool
def search_docs(query: str) -> str:
    """로컬 문서에서 관련 내용을 BM25 키워드 검색으로 찾아 반환한다."""
    ...

@tool
def check_resolved(answer: str, query: str) -> str:
    """생성된 답변으로 문제 해결이 가능한지 판단한다."""
    ...

@tool
def create_ticket(query: str, summary: str) -> str:
    """미해결 케이스의 티켓을 생성하고 인계 메시지를 반환한다."""
    ...
```

### Step 3. 멀티 에이전트 구성

`create_agent`로 4개 Agent를 각각 생성한다. 모든 Agent는 동일한 Samsung 사내 AI 모델을 사용한다.

```python
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
import os, uuid
from dotenv import load_dotenv

load_dotenv(".env")

def make_model(temperature=0):
    return ChatOpenAI(
        model=os.getenv("model"),
        base_url=os.getenv("api_base_url"),
        default_headers={
            'x-dep-ticekt': os.getenv("credential_key"),
            'Send-System-Name': os.getenv("send_system_name"),
            'User-Id': os.getenv("user_id"),
            'User-Type': "AD_ID",
            'Prompt-Msg-Id': str(uuid.uuid4()),
            'Completion-Msg-Id': str(uuid.uuid4()),
        },
        temperature=temperature,
    )

classifier_agent = create_agent(
    model=make_model(),
    tools=[classify_query],
    system_prompt="...",  # few-shot 예시 포함
)

rag_agent = create_agent(
    model=make_model(),
    tools=[search_docs],
    system_prompt="...",
)

answer_agent = create_agent(
    model=make_model(temperature=0.3),
    tools=[check_resolved],
    system_prompt="...",  # 에스컬레이션 판단 기준 명시
)

escalation_agent = create_agent(
    model=make_model(),
    tools=[create_ticket],
    system_prompt="...",
)
```

### Step 4. 미들웨어 구성 및 에이전트 완성

오케스트레이터 함수로 Agent 실행 순서와 조건 분기를 연결한다.

```python
from langgraph.checkpoint.memory import InMemorySaver

checkpointer = InMemorySaver()

def sanitize_input(query: str) -> str:
    """입력 전처리 — 길이 제한 및 특수 패턴 필터링"""
    return query[:500].strip()

def run_cs_pipeline(query: str, thread_id: str) -> str:
    config = {"configurable": {"thread_id": thread_id}}
    query = sanitize_input(query)

    # Step 1: 분류
    classify_result = classifier_agent.invoke(...)

    # Step 2: RAG 검색
    search_result = rag_agent.invoke(...)

    # Step 3: RAG 결과 없으면 바로 에스컬레이션
    if not search_result.found:
        return escalation_agent.invoke(...)

    # Step 4: 답변 생성
    answer_result = answer_agent.invoke(...)

    # Step 5: 조건 분기
    if answer_result.should_escalate or answer_result.confidence < 0.7:
        return escalation_agent.invoke(...)

    return answer_result.answer
```

### Step 5. Streamlit UI 제작

```python
import streamlit as st

st.title("삼성전자 CS Agent")

# 세션 초기화
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

# 대화 이력 표시
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 사용자 입력
if query := st.chat_input("문의 내용을 입력하세요"):
    st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("assistant"):
        with st.spinner("답변 생성 중..."):
            response = run_cs_pipeline(query, st.session_state.thread_id)
        st.write(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
```

---

## 5. 폴더 구조

```
samsung-cs-agent/
  data/
    galaxy_faq.txt
    product_manual.txt
    defect_history.txt
    as_policy.txt
  rag.py              # 파일 로딩, 청킹, BM25 검색 통합
  agents.py           # 4개 Agent 정의 + tool 함수 통합
  pipeline.py         # 오케스트레이터 함수
  app.py              # Streamlit UI
  requirements.txt
```

> 기존 명세서의 `rag/loader.py` + `rag/retriever.py` + `agents/` 4개 파일 구조를 `rag.py` + `agents.py` 2개 파일로 통합하여 코드량을 줄인다.

---

## 6. 기술 스택

| 구분 | 사용 기술 |
|---|---|
| LLM | Samsung 사내 AI (단일 모델, ChatOpenAI 호환 API) |
| Agent Framework | LangChain `create_agent` |
| 검색 | BM25 키워드 검색 (rank_bm25, 벡터 DB 없음) |
| Memory | `InMemorySaver` (세션 내 대화 맥락 유지) |
| UI | Streamlit |
| 개발 환경 | Python 3.11, venv, VS Code |

---

## 7. 기대 효과

| 항목 | 현재 | 목표 |
|---|---|---|
| 반복 문의 처리 | 상담원 직접 응대 | 70% 자동화 |
| 1차 해결률 | 55% | 85% |
| 평균 응답 시간 | 5분 | 10초 |
| 에스컬레이션 누락 | 간헐적 발생 | confidence 기반 안전망으로 0건 목표 |

단순 자동화가 아니라 **판단하는 시스템**을 만드는 것이 이 프로젝트의 핵심이다.

---

## 8. 주요 리스크 및 대비

| 리스크 | 대비 |
|---|---|
| Agent 출력이 자유형식이라 파싱 실패 | 모든 Agent 출력을 `@dataclass`로 구조화 |
| RAG 검색 결과 없을 때 빈 컨텍스트 전달 | `found` 플래그로 fallback 분기 처리 |
| 에스컬레이션 판단 기준 모호 | few-shot 예시 + confidence 임계값 0.7 설정 |
| BM25 키워드 검색 정확도 한계 | 검색 결과 없으면 안전하게 에스컬레이션 처리 |
| 대화 맥락 유실 | `InMemorySaver` + `thread_id`로 세션 관리 |
| 프롬프트 인젝션 | 입력 전처리 (500자 제한, 특수 패턴 필터링) |
