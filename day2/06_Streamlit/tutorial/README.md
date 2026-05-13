# Streamlit 단계별 학습 가이드

이 폴더는 Streamlit을 처음 배우는 분들을 위한 **점진적 학습 자료**입니다.
각 파일을 순서대로 실행하며 개념을 익혀 주세요.

## 학습 순서

| 파일 | 주제 | 핵심 개념 |
|------|------|-----------|
| `step1_ui_basics.py` | UI 기초 | 텍스트, 위젯, 피드백 메시지 |
| `step2_layout.py` | 레이아웃 | columns, tabs, sidebar, expander |
| `step3_session_state.py` | 상태 관리 | session_state, rerun 메커니즘 |
| `step4_chat_ui.py` | 채팅 UI | chat_message, chat_input, 대화 기록 |
| `step5_agent.py` | 에이전트 연동 | cache_resource, invoke, thread_id |
| `step6_streaming.py` | 스트리밍 응답 | stream(), AIMessageChunk, st.empty() |
| `step7_complete.py` | 완성형 챗봇 | 도구 호출 시각화 + 전체 통합 |

## 실행 방법

```bash
# 각 파일을 개별적으로 실행합니다
streamlit run step1_ui_basics.py
streamlit run step2_layout.py
# ...
```

## 폴더 구조 안내

```
day2/06_Streamlit/
├── tutorial/          ← 지금 보고 있는 학습 폴더
│   ├── step1~7 ...
└── basic_agent/       ← 완성형 RAG+도구+미들웨어 에이전트 앱 (참고용)
```

## 사전 준비

프로젝트 루트의 `.env` 파일에 API 키가 설정되어 있어야 합니다.

```
credential_key=your-openai-api-key
model=gpt-4o-mini
```

---

> **자세한 개념 설명은 각 step의 `.md` 파일을 함께 읽어 주세요.**
> 예: `step1_ui_basics.py` ↔ `step1_ui_basics.md`
