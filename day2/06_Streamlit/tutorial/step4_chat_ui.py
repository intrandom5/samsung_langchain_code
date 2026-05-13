"""
Step 4: 채팅 UI 구성
=====================
실제 AI 연결 없이, 순수 Streamlit UI만으로 채팅 인터페이스를 만듭니다.

실행 방법:
    streamlit run step4_chat_ui.py

📌 이번 단계에서 배우는 것:
    - st.chat_message() : "user"와 "assistant" 말풍선
    - st.chat_input()   : 화면 하단에 고정된 입력창
    - 메시지 기록을 session_state 리스트로 관리하는 패턴

💡 핵심 패턴:
    1. messages 리스트를 session_state에 저장
    2. 리런 때마다 messages 전체를 반복해서 화면에 표시
    3. 새 입력이 오면 messages에 추가 → 자동으로 화면에 반영

    (AI 연동은 Step 5에서 합니다. 여기서는 "에코 봇"으로 UI만 완성합니다)
"""
import time
import random

import streamlit as st

st.set_page_config(page_title="Step 4: 채팅 UI", page_icon="💬", layout="wide")
st.title("💬 채팅 UI 구성")

# ── 채팅 UI 핵심 위젯 소개 ────────────────────────────────────────────────────
with st.expander("📌 채팅 위젯 핵심 설명 (클릭해서 펼치기)", expanded=True):
    st.markdown("""
    **st.chat_message(role)**
    - `role`에 `"user"` 또는 `"assistant"`를 넣으면 각각 다른 스타일의 말풍선이 만들어집니다
    - `with` 블록 안에 `st.write()`, `st.markdown()` 등으로 내용을 채웁니다
    - 아이콘이 자동으로 표시됩니다 (user: 사람 아이콘, assistant: 로봇 아이콘)

    **st.chat_input(placeholder)**
    - 항상 화면 **맨 아래에 고정**됩니다
    - 사용자가 입력하고 Enter를 누르면 입력한 문자열을 반환합니다
    - 입력이 없으면 `None`을 반환합니다 (→ `if prompt :=` 패턴 사용)
    """)

st.divider()

# ═══════════════════════════════════════════════════════════════════════════════
# 메시지 기록 초기화
# ═══════════════════════════════════════════════════════════════════════════════
# "messages"가 없을 때만 빈 리스트로 초기화 (Step 3의 session_state 패턴!)
if "messages" not in st.session_state:
    st.session_state.messages = []
    # 시작 인사말을 미리 추가해둡니다
    st.session_state.messages.append({
        "role": "assistant",
        "content": "안녕하세요! 저는 에코 봇입니다. 무엇이든 입력해보세요. (Step 5에서 실제 AI로 교체됩니다)"
    })

# ── 사이드바 ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ 채팅 설정")

    if st.button("🗑️ 대화 초기화", use_container_width=True):
        # messages 리스트를 비워서 대화를 초기화합니다
        st.session_state.messages = []
        st.rerun()

    st.divider()

    # 현재 대화 통계
    total = len(st.session_state.messages)
    user_count = sum(1 for m in st.session_state.messages if m["role"] == "user")
    st.metric("총 메시지 수", total)
    st.metric("내가 보낸 메시지", user_count)

    st.divider()

    # 봇 응답 스타일 선택 (UI 실습용)
    bot_style = st.radio(
        "봇 응답 스타일",
        options=["에코 (입력 그대로 반복)", "랜덤 응답", "타이핑 효과"],
        index=2,
    )

# ═══════════════════════════════════════════════════════════════════════════════
# 기존 대화 내용 표시
# ═══════════════════════════════════════════════════════════════════════════════
# 리런될 때마다 저장된 messages를 처음부터 다시 그립니다.
# 이것이 대화 기록이 유지되는 원리입니다.
for msg in st.session_state.messages:
    # msg["role"]이 "user"면 사용자 말풍선, "assistant"면 AI 말풍선
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ═══════════════════════════════════════════════════════════════════════════════
# 새 메시지 처리
# ═══════════════════════════════════════════════════════════════════════════════
# := 는 "바다코끼리 연산자(walrus operator)". 값을 변수에 대입하면서 동시에 조건 검사
# prompt가 None이 아닐 때(= 사용자가 입력했을 때)만 if 블록 실행
if prompt := st.chat_input("메시지를 입력하세요..."):

    # ── 1. 사용자 메시지 처리 ──────────────────────────────────────────────────
    # 화면에 사용자 말풍선으로 즉시 표시
    with st.chat_message("user"):
        st.markdown(prompt)

    # session_state에 저장 (다음 리런 때도 이 메시지가 표시됨)
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
    })

    # ── 2. 봇 응답 생성 ────────────────────────────────────────────────────────
    # (여기서는 실제 AI 없이 간단한 규칙으로 응답을 만듭니다)
    if bot_style == "에코 (입력 그대로 반복)":
        response = f"에코: {prompt}"

    elif bot_style == "랜덤 응답":
        canned_responses = [
            f"'{prompt}'라고 하셨군요! 흥미롭네요. 🤔",
            "좋은 말씀입니다! (아직 AI가 연결되지 않았습니다)",
            f"**{prompt}** — 잘 받았습니다!",
            "Step 5에서 진짜 AI가 여기에 응답할 거예요. 😊",
            "네, 알겠습니다! (에코 봇은 실제로 이해하지 못합니다 😅)",
        ]
        response = random.choice(canned_responses)

    else:  # 타이핑 효과
        response = f"입력하신 내용 '{prompt}'을 처리했습니다! (타이핑 효과 예시)"

    # ── 3. 봇 응답 표시 ────────────────────────────────────────────────────────
    with st.chat_message("assistant"):
        if bot_style == "타이핑 효과":
            # st.empty() : 내용을 나중에 채울 수 있는 빈 자리(placeholder)를 만듭니다
            # 스트리밍이나 타이핑 효과를 줄 때 이렇게 활용합니다 (Step 6에서 더 자세히)
            placeholder = st.empty()
            typed_text = ""

            for char in response:
                typed_text += char
                # placeholder를 계속 업데이트해서 타이핑 효과를 냅니다
                # "▌"는 커서 역할을 합니다
                placeholder.markdown(typed_text + "▌")
                time.sleep(0.03)  # 글자마다 30ms 지연

            # 타이핑 완료: 커서(▌) 제거
            placeholder.markdown(typed_text)

        else:
            st.markdown(response)

    # ── 4. 봇 응답도 기록에 저장 ───────────────────────────────────────────────
    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
    })

    # ※ 여기서는 st.rerun()을 호출하지 않아도 됩니다.
    #   st.chat_input()에 입력이 들어오면 Streamlit이 자동으로 리런하기 때문입니다.
