"""
Step 2: 레이아웃 구성
=====================
위젯들을 원하는 위치에 배치하는 방법을 배웁니다.

실행 방법:
    streamlit run step2_layout.py

📌 이번 단계에서 배우는 것:
    - st.columns()  : 화면을 여러 열(column)로 나누기
    - st.tabs()     : 탭 인터페이스 만들기
    - st.sidebar    : 왼쪽 사이드바 활용
    - st.expander() : 접을 수 있는 섹션 만들기
    - st.container(): 요소들을 논리적으로 묶기

📖 자세한 설명 → step2_layout.md
"""
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Step 2: 레이아웃", page_icon="🔲", layout="wide")
st.title("🔲 레이아웃 구성")

# ═══════════════════════════════════════════════════════════════════════════════
# 1. 컬럼(Columns) — 화면 가로 분할
# ═══════════════════════════════════════════════════════════════════════════════
st.header("1. st.columns() — 화면 가로 분할")
st.write("""
`st.columns(n)` 으로 화면을 n개의 열로 나눌 수 있습니다.
`with col:` 블록 안에 위젯을 넣으면 해당 열에 배치됩니다.
""")

# 균등 3분할
st.subheader("균등 분할")
col1, col2, col3 = st.columns(3)
with col1:
    # delta: 변화량. 양수 → 초록 화살표, 음수 → 빨간 화살표
    st.metric("🌡️ 온도", "23°C", delta="+2°C")
with col2:
    st.metric("💧 습도", "65%", delta="-5%")
with col3:
    st.metric("🌫️ 미세먼지", "좋음", delta=None)  # delta 없으면 화살표 미표시

# 비율 지정 분할
st.subheader("비율 지정 분할 ([2, 1])")
st.write("리스트로 비율을 지정할 수 있습니다. [2, 1]이면 2:1 비율로 분할됩니다.")

left, right = st.columns([2, 1])
with left:
    # 이 블록 안의 모든 위젯은 왼쪽 열(화면의 2/3)에 표시됩니다
    st.info("왼쪽 영역 (화면의 2/3)\n\nst.columns([2, 1])의 첫 번째 열입니다.")
    name_in_left = st.text_input("이름 (왼쪽 열에 배치된 위젯)")
with right:
    st.info("오른쪽 영역 (화면의 1/3)")
    if name_in_left:
        st.success(f"안녕하세요, {name_in_left}님!")

st.divider()

# ═══════════════════════════════════════════════════════════════════════════════
# 2. 탭(Tabs) — 내용을 탭으로 구분
# ═══════════════════════════════════════════════════════════════════════════════
st.header("2. st.tabs() — 탭 인터페이스")
st.write("""
`st.tabs(["탭1", "탭2", ...])` 로 탭 메뉴를 만들 수 있습니다.
한 화면에 많은 정보를 표시할 때 탭으로 정리하면 깔끔합니다.
""")

# 샘플 데이터 준비
sample_df = pd.DataFrame({
    "이름": ["Alice", "Bob", "Carol", "Dave", "Eve"],
    "부서": ["개발", "디자인", "마케팅", "개발", "디자인"],
    "점수": [95, 87, 92, 78, 88],
})

tab_data, tab_chart, tab_info = st.tabs(["📊 데이터 테이블", "📈 차트", "ℹ️ 설명"])

with tab_data:
    st.write("인터랙티브 데이터프레임입니다. 열 헤더를 클릭해 정렬할 수 있습니다.")
    st.dataframe(sample_df, use_container_width=True)

with tab_chart:
    st.write("점수를 막대 차트로 시각화합니다.")
    # 인덱스를 이름으로 설정하고 점수 열만 차트로 표시
    chart_df = sample_df.set_index("이름")[["점수"]]
    st.bar_chart(chart_df)

with tab_info:
    st.markdown("""
    **데이터 설명**
    - 총 5명의 직원 점수 데이터입니다.
    - 점수 범위: 0 ~ 100
    - 탭을 클릭해 데이터와 차트를 전환해보세요.
    """)

st.divider()

# ═══════════════════════════════════════════════════════════════════════════════
# 3. 사이드바(Sidebar) — 왼쪽 고정 패널
# ═══════════════════════════════════════════════════════════════════════════════
st.header("3. st.sidebar — 사이드바")
st.write("""
`with st.sidebar:` 블록 안의 위젯은 왼쪽 사이드바에 표시됩니다.
보통 필터, 설정 옵션, 네비게이션 등을 배치합니다.
👉 **왼쪽 사이드바를 열어보세요!**
""")

# with 블록 없이 st.sidebar.XXX() 형태로도 사용 가능
with st.sidebar:
    st.header("⚙️ 필터 설정")
    st.caption("사이드바에 설정 옵션을 배치하면 메인 화면을 넓게 사용할 수 있습니다.")

    st.divider()

    # 사이드바 안에 배치된 위젯들 (메인 화면과 동일하게 사용 가능)
    selected_dept = st.multiselect(
        "부서 필터",
        options=["개발", "디자인", "마케팅"],
        default=["개발", "디자인", "마케팅"],
    )
    min_score = st.slider("최소 점수", 0, 100, 70)

    st.divider()
    st.info("📌 사이드바는 어느 화면에서든 항상 접근할 수 있습니다.")

# 사이드바 필터 적용 결과를 메인 화면에 표시
filtered_df = sample_df[
    (sample_df["부서"].isin(selected_dept)) &
    (sample_df["점수"] >= min_score)
]
st.subheader("사이드바 필터 적용 결과")
st.write(f"조건에 맞는 직원 수: **{len(filtered_df)}명**")
st.dataframe(filtered_df, use_container_width=True)

st.divider()

# ═══════════════════════════════════════════════════════════════════════════════
# 4. 익스팬더(Expander) — 접을 수 있는 섹션
# ═══════════════════════════════════════════════════════════════════════════════
st.header("4. st.expander() — 접을 수 있는 섹션")
st.write("""
`st.expander("제목")`으로 클릭하면 펼쳐지는 섹션을 만듭니다.
길거나 보조적인 내용을 숨겨두고 필요할 때만 보여줄 때 유용합니다.
""")

# expanded=True 이면 처음부터 펼쳐진 상태
with st.expander("📋 원본 데이터 전체 보기 (클릭해서 펼치기)", expanded=False):
    st.write("이 내용은 평소에 숨겨져 있습니다. 클릭하면 보입니다.")
    st.dataframe(sample_df, use_container_width=True)
    st.code("""
# 이런 코드도 넣을 수 있어요
import pandas as pd
df = pd.read_csv("data.csv")
    """)

with st.expander("❓ 도움말", expanded=False):
    st.markdown("""
    **Q: 사이드바 필터가 작동하지 않아요.**
    A: 사이드바에서 부서 또는 최소 점수를 조정해 보세요.

    **Q: 탭이 보이지 않아요.**
    A: "2. st.tabs()" 섹션을 스크롤해서 찾아보세요.
    """)

st.divider()

# ═══════════════════════════════════════════════════════════════════════════════
# 5. 레이아웃 조합 실습
# ═══════════════════════════════════════════════════════════════════════════════
st.header("5. 레이아웃 조합 실습")
st.write("columns + tabs + expander를 조합한 대시보드 형태 예시입니다.")

# 상단: 주요 지표 3열 배치
m1, m2, m3, m4 = st.columns(4)
m1.metric("총 직원수", f"{len(filtered_df)}명")
m2.metric("평균 점수", f"{filtered_df['점수'].mean():.1f}점" if len(filtered_df) else "—")
m3.metric("최고 점수", f"{filtered_df['점수'].max()}점" if len(filtered_df) else "—")
m4.metric("최저 점수", f"{filtered_df['점수'].min()}점" if len(filtered_df) else "—")

# 하단: 탭으로 상세 정보
t1, t2 = st.tabs(["📋 목록", "📊 차트"])
with t1:
    if len(filtered_df):
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.warning("조건에 맞는 직원이 없습니다. 사이드바에서 필터를 조정해보세요.")
with t2:
    if len(filtered_df):
        st.bar_chart(filtered_df.set_index("이름")[["점수"]])
    else:
        st.warning("표시할 데이터가 없습니다.")
