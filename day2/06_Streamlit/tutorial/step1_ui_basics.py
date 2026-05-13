"""
Step 1: Streamlit UI 기초
=========================
다양한 UI 요소(위젯)의 종류와 사용법을 익힙니다.

실행 방법:
    streamlit run step1_ui_basics.py

💡 핵심 원리:
    Streamlit은 사용자가 무언가를 조작할 때마다 이 스크립트를
    위에서 아래로 처음부터 다시 실행합니다.
    각 위젯은 사용자의 현재 입력값을 '반환(return)'하므로,
    변수에 저장해서 그 값을 사용합니다.

📖 자세한 개념 설명 → step1_ui_basics.md
"""
import streamlit as st
import pandas as pd

# ── 페이지 설정 ──────────────────────────────────────────────────────────────
# 반드시 다른 st 명령어보다 먼저 호출해야 합니다
st.set_page_config(
    page_title="Step 1: UI 기초",
    page_icon="🎨",
    layout="wide",           # "centered"(기본) 또는 "wide"
    initial_sidebar_state="collapsed",  # 사이드바 시작 상태
)

# ═══════════════════════════════════════════════════════════════════════════════
# 1. 텍스트 요소
# ═══════════════════════════════════════════════════════════════════════════════
st.title("🎨 Streamlit UI 기초")  # 가장 큰 제목 (H1)

st.header("1. 텍스트 요소")  # 섹션 제목 (H2)
st.subheader("다양한 방식으로 텍스트를 표시할 수 있습니다")  # 소제목 (H3)

# st.write() : 가장 범용적인 함수. 텍스트, 숫자, 데이터프레임, 딕셔너리 등 거의 모든 것 출력 가능
st.write("**st.write()** : 텍스트, 숫자, 데이터프레임 등 무엇이든 출력합니다.")

# st.markdown() : 마크다운 문법 적용
st.markdown("""
**굵게**, *기울임*, `인라인 코드`, [링크](https://streamlit.io)
> 인용문도 됩니다
""")

# st.caption() : 회색 작은 글씨로 부가 설명
st.caption("st.caption() : 이미지 설명, 출처 표기 등에 활용합니다.")

# st.code() : 코드 하이라이팅과 복사 버튼 제공
st.code("""
# Python 예시
def greet(name: str) -> str:
    return f"안녕하세요, {name}님!"
""", language="python")

st.divider()  # 구분선

# ═══════════════════════════════════════════════════════════════════════════════
# 2. 입력 위젯
# ═══════════════════════════════════════════════════════════════════════════════
st.header("2. 입력 위젯")
st.write("""
위젯은 사용자의 입력을 받고, 그 값을 **반환(return)** 합니다.
반환된 값을 변수에 저장해서 사용합니다.

```python
# 예시: text_input은 사용자가 입력한 문자열을 반환합니다
name = st.text_input("이름")  # name에 사용자 입력값 저장
```
""")

col1, col2 = st.columns(2)  # 화면을 2열로 나눔

with col1:
    st.subheader("텍스트/숫자 입력")

    # 한 줄 텍스트 입력. 빈 문자열("")을 반환하다가 입력하면 해당 문자열 반환
    name = st.text_input(
        label="이름",           # 위젯 위에 표시되는 라벨
        placeholder="홍길동",   # 입력 전 흐릿하게 표시되는 힌트 텍스트
        max_chars=20,           # 최대 글자 수 제한
    )

    # 여러 줄 텍스트 입력
    bio = st.text_area("자기소개", placeholder="간단히 소개해주세요.", height=100)

    # 숫자 입력 (증감 버튼 포함)
    age = st.number_input("나이", min_value=0, max_value=150, value=25, step=1)

    # 날짜 선택기
    import datetime
    birthday = st.date_input("생일", value=datetime.date(1990, 1, 1))

with col2:
    st.subheader("선택 위젯")

    # 드롭다운 선택 (하나만 선택)
    language = st.selectbox(
        "주력 언어",
        options=["Python", "JavaScript", "Java", "Go", "Rust"],
        index=0,   # 기본 선택 항목의 인덱스
    )

    # 다중 선택
    frameworks = st.multiselect(
        "사용 프레임워크",
        options=["FastAPI", "Django", "Flask", "LangChain", "Streamlit"],
        default=["Streamlit"],  # 처음부터 선택된 값
    )

    # 라디오 버튼 (하나만 선택)
    experience = st.radio(
        "경력",
        options=["신입", "1~3년", "3~5년", "5년 이상"],
        horizontal=True,   # 가로로 나열 (기본값은 세로)
    )

    # 체크박스 (True/False 반환)
    agree = st.checkbox("개인정보 수집에 동의합니다")

    # 슬라이더 (최솟값~최댓값 사이 숫자 반환)
    skill_level = st.slider("실력 수준 (1~10)", min_value=1, max_value=10, value=5)

st.divider()

# ═══════════════════════════════════════════════════════════════════════════════
# 3. 위젯 반환값 활용하기
# ═══════════════════════════════════════════════════════════════════════════════
st.header("3. 위젯 반환값 활용하기")
st.write("위에서 입력한 값들이 아래에 실시간으로 반영됩니다.")

# 입력값이 있을 때만 표시 (name이 빈 문자열이면 falsy)
if name:
    st.success(f"""
    **프로필 요약**
    - 이름: {name}
    - 나이: {age}세
    - 생일: {birthday}
    - 주력 언어: {language}
    - 프레임워크: {', '.join(frameworks) if frameworks else '없음'}
    - 경력: {experience}
    - 실력: {'⭐' * skill_level}
    - 동의 여부: {'✅ 동의' if agree else '❌ 미동의'}
    """)
else:
    st.info("위에서 이름을 입력하면 프로필 요약이 표시됩니다.")

st.divider()

# ═══════════════════════════════════════════════════════════════════════════════
# 4. 버튼
# ═══════════════════════════════════════════════════════════════════════════════
st.header("4. 버튼")
st.write("""
버튼은 클릭하면 `True`를 반환하고, 그렇지 않으면 `False`를 반환합니다.
`if st.button(...):`으로 클릭 시 실행할 코드를 감쌉니다.

⚠️ **주의**: 버튼을 클릭하면 페이지가 리런되면서 버튼은 다시 `False`가 됩니다.
버튼 클릭 결과를 유지하려면 Session State가 필요합니다 (Step 3 참조).
""")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🎉 기본 버튼"):
        st.balloons()  # 풍선 효과!
with col2:
    if st.button("⚠️ 보조 버튼", type="secondary"):
        st.toast("보조 버튼 클릭!")  # 우상단 알림 메시지
with col3:
    if st.button("🗑️ 위험 버튼", type="primary", use_container_width=True):
        st.warning("위험한 작업 전 확인이 필요합니다!")

st.divider()

# ═══════════════════════════════════════════════════════════════════════════════
# 5. 피드백 메시지
# ═══════════════════════════════════════════════════════════════════════════════
st.header("5. 피드백 메시지")
st.write("사용자에게 결과나 상태를 알릴 때 사용합니다.")

st.success("✅ 작업이 성공적으로 완료되었습니다! (st.success)")
st.info("ℹ️ 참고 정보를 표시합니다. (st.info)")
st.warning("⚠️ 주의가 필요한 상황입니다. (st.warning)")
st.error("❌ 오류가 발생했습니다. (st.error)")

st.divider()

# ═══════════════════════════════════════════════════════════════════════════════
# 6. 데이터 표시
# ═══════════════════════════════════════════════════════════════════════════════
st.header("6. 데이터 표시")

col1, col2 = st.columns(2)
with col1:
    st.subheader("st.dataframe() - 인터랙티브 표")
    df = pd.DataFrame({
        "이름": ["Alice", "Bob", "Carol", "Dave"],
        "점수": [95, 87, 92, 78],
        "등급": ["A", "B", "A", "C"],
    })
    # use_container_width=True : 부모 요소 너비에 맞게 늘림
    st.dataframe(df, use_container_width=True)

with col2:
    st.subheader("st.metric() - 수치 지표")
    # delta: 변화량 (양수면 초록, 음수면 빨강)
    st.metric("매출", "₩1,234,000", delta="+12.3%")
    st.metric("방문자", "5,432명", delta="-3.1%")
    st.metric("만족도", "4.8 / 5.0", delta="+0.2")
