"""
Step 3: Session State — 상태 관리
==================================
페이지가 리런(rerun)될 때도 값이 유지되는 Session State를 배웁니다.

실행 방법:
    streamlit run step3_session_state.py

📌 이번 단계의 핵심 질문:
    "버튼을 10번 클릭하면 카운터가 10이 되어야 하는데, 왜 항상 1일까요?"
    → 이 문제를 Session State로 해결합니다.

📖 자세한 개념 설명 → step3_session_state.md
"""
import streamlit as st

st.set_page_config(page_title="Step 3: Session State", page_icon="🧠", layout="wide")
st.title("🧠 Session State — 상태 관리")

# ═══════════════════════════════════════════════════════════════════════════════
# 1. 문제 상황: 일반 변수는 리런 시 초기화됨
# ═══════════════════════════════════════════════════════════════════════════════
st.header("1. ❌ 문제: 일반 변수는 리런 때마다 초기화됩니다")

st.warning("""
**Streamlit의 동작 방식 (리마인드)**
버튼 클릭, 텍스트 입력 등 사용자 조작이 있을 때마다 이 스크립트 전체가 처음부터 다시 실행됩니다.
따라서, 일반 Python 변수는 리런할 때마다 선언된 초기값으로 돌아갑니다.
""")

# 아래 변수는 리런할 때마다 항상 0으로 초기화됩니다
broken_count = 0

col1, col2 = st.columns([1, 3])
with col1:
    if st.button("➕ 증가 (❌ 고장난 버전)"):
        broken_count += 1   # 0 + 1 = 1이 되지만... 다음 리런 때 다시 0이 됨

with col2:
    # 버튼을 아무리 눌러도 항상 1 또는 0만 표시됩니다
    st.write(f"카운터 값: **{broken_count}** (항상 0 또는 1만 표시됩니다)")
    st.caption("👆 버튼을 여러 번 눌러보세요. 절대 2 이상이 되지 않습니다.")

st.divider()

# ═══════════════════════════════════════════════════════════════════════════════
# 2. 해결책: st.session_state 사용
# ═══════════════════════════════════════════════════════════════════════════════
st.header("2. ✅ 해결: st.session_state로 값을 유지합니다")

st.info("""
`st.session_state`는 리런해도 사라지지 않는 **딕셔너리** 같은 특별한 저장소입니다.
- 브라우저 탭을 새로 고침하면 초기화됩니다 (탭 단위로 유지)
- 여러 사용자가 동시에 쓰면 각자의 session_state를 가집니다 (격리됨)
""")

# session_state 초기화 패턴:
# "count"라는 키가 아직 없을 때만 초기값을 설정합니다.
# 이 조건문이 없으면 리런할 때마다 0으로 덮어써버립니다!
if "count" not in st.session_state:
    st.session_state.count = 0  # 처음 실행될 때 딱 한 번만 0으로 초기화

col1, col2, col3 = st.columns([1, 1, 3])
with col1:
    if st.button("➕ 증가 (✅ 올바른 버전)"):
        # session_state에 저장된 값을 1 증가
        # 리런 후에도 이 값은 유지됩니다
        st.session_state.count += 1
with col2:
    if st.button("🔄 초기화"):
        st.session_state.count = 0
with col3:
    # session_state의 값을 읽어서 표시합니다
    st.metric("카운터", st.session_state.count)
    st.caption("이제 버튼을 누를수록 숫자가 계속 올라갑니다!")

st.divider()

# ═══════════════════════════════════════════════════════════════════════════════
# 3. session_state 사용 문법
# ═══════════════════════════════════════════════════════════════════════════════
st.header("3. session_state 사용 문법")

st.code("""
# ── 초기화 ──────────────────────────────────────────────
# 방법 1: 딕셔너리 스타일
if "my_key" not in st.session_state:
    st.session_state["my_key"] = 초기값

# 방법 2: 속성 스타일 (더 자주 쓰임)
if "my_key" not in st.session_state:
    st.session_state.my_key = 초기값

# ── 읽기 ──────────────────────────────────────────────
value = st.session_state.my_key          # 속성 스타일
value = st.session_state["my_key"]       # 딕셔너리 스타일

# ── 쓰기(수정) ────────────────────────────────────────
st.session_state.my_key = 새로운값
st.session_state["my_key"] = 새로운값

# ── 삭제 ──────────────────────────────────────────────
del st.session_state.my_key
""", language="python")

st.divider()

# ═══════════════════════════════════════════════════════════════════════════════
# 4. 실용 예제: 단계별 폼 (여러 상태를 동시에 관리)
# ═══════════════════════════════════════════════════════════════════════════════
st.header("4. 실용 예제: 단계별 입력 폼")
st.write("여러 session_state를 조합해 다단계 폼을 구현합니다.")

# 여러 상태를 함께 초기화할 때는 이렇게 묶어서 쓰면 편합니다
for key, default in [
    ("step", 1),             # 현재 단계 (1, 2, 3)
    ("form_name", ""),       # 1단계에서 입력한 이름
    ("form_age", 0),         # 2단계에서 입력한 나이
    ("form_goal", ""),       # 2단계에서 입력한 목표
]:
    if key not in st.session_state:
        st.session_state[key] = default

# 진행 상황 표시
current_step = st.session_state.step
st.progress(current_step / 3, text=f"단계 {current_step} / 3")

# 단계별 폼 표시
if current_step == 1:
    st.subheader("1단계: 기본 정보")
    name_input = st.text_input("이름을 입력하세요", value=st.session_state.form_name)

    if st.button("다음 →", type="primary"):
        if name_input.strip():  # 공백만 있는 경우 제외
            # 입력값을 session_state에 저장하고 다음 단계로
            st.session_state.form_name = name_input
            st.session_state.step = 2
            # st.rerun(): 즉시 페이지를 다시 실행해서 UI 변경사항을 반영합니다
            st.rerun()
        else:
            st.warning("이름을 입력해주세요!")

elif current_step == 2:
    st.subheader("2단계: 추가 정보")
    st.write(f"안녕하세요, **{st.session_state.form_name}**님!")

    age_input = st.number_input("나이", min_value=1, max_value=150, value=max(st.session_state.form_age, 1))
    goal_input = st.text_area("학습 목표", value=st.session_state.form_goal, placeholder="Streamlit으로 AI 앱 만들기")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← 이전"):
            st.session_state.step = 1
            st.rerun()
    with col2:
        if st.button("다음 →", type="primary"):
            if goal_input.strip():
                st.session_state.form_age = age_input
                st.session_state.form_goal = goal_input
                st.session_state.step = 3
                st.rerun()
            else:
                st.warning("학습 목표를 입력해주세요!")

elif current_step == 3:
    st.subheader("3단계: 확인")
    st.success("입력이 완료되었습니다! 내용을 확인해주세요.")

    # 지금까지 입력한 내용을 요약해서 표시
    st.markdown(f"""
    | 항목 | 내용 |
    |------|------|
    | 이름 | {st.session_state.form_name} |
    | 나이 | {st.session_state.form_age}세 |
    | 학습 목표 | {st.session_state.form_goal} |
    """)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← 이전"):
            st.session_state.step = 2
            st.rerun()
    with col2:
        if st.button("✅ 제출", type="primary"):
            st.balloons()
            st.success("제출 완료! 처음으로 돌아갑니다.")
            # 모든 폼 상태를 초기화
            for key in ["step", "form_name", "form_age", "form_goal"]:
                del st.session_state[key]
            st.rerun()

st.divider()

# ═══════════════════════════════════════════════════════════════════════════════
# 5. 디버깅: 현재 session_state 전체 보기
# ═══════════════════════════════════════════════════════════════════════════════
st.header("5. 🔍 현재 session_state 내용 (디버깅 도구)")
st.write("개발할 때 session_state에 어떤 값이 들어 있는지 확인하는 데 유용합니다.")

with st.expander("session_state 내용 보기"):
    # dict(st.session_state) : session_state를 일반 딕셔너리로 변환해서 JSON으로 표시
    st.json(dict(st.session_state))
    st.caption("탭을 새로고침하면 이 내용이 초기화됩니다.")
