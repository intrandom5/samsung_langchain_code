"""
CSV 데이터 분석기
- CSV 파일을 업로드하면 데이터 미리보기, 시각화, AI 인사이트를 제공합니다.
- 실행 방법: streamlit run app.py
"""
import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from dotenv import load_dotenv, find_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# 한글 폰트 설정 (matplotlib 한글 깨짐 방지)
matplotlib.rcParams["font.family"] = "DejaVu Sans"

# .env 파일 불러오기 (프로젝트 루트에서 자동으로 찾음)
load_dotenv(find_dotenv())

# ── 페이지 설정 ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="CSV 분석기", page_icon="📊", layout="wide")

st.title("📊 CSV 데이터 분석기")
st.caption("CSV 파일을 업로드하면 AI가 데이터를 분석해드립니다.")


# ── LLM 초기화 (캐시로 한 번만 로드) ─────────────────────────────────────────
@st.cache_resource
def load_model():
    return ChatOpenAI(
        model=os.getenv("model"),
        api_key=os.getenv("credential_key"),
        temperature=0.7,
    )


# ── CSV 파일 업로드 ───────────────────────────────────────────────────────────
uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type=["csv"])

if uploaded_file is not None:
    # CSV 읽기
    df = pd.read_csv(uploaded_file)

    st.success(f"파일 로드 완료! {len(df)}행 x {len(df.columns)}열")

    # ── 탭 구성 ───────────────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["📋 데이터 미리보기", "📈 시각화", "🤖 AI 분석"])

    # ── 탭 1: 데이터 미리보기 ─────────────────────────────────────────────────
    with tab1:
        # 핵심 지표 3개를 나란히 표시 (st.metric)
        col1, col2, col3 = st.columns(3)
        col1.metric("총 행 수", f"{len(df):,}")
        col2.metric("총 열 수", len(df.columns))
        col3.metric("결측치 수", int(df.isnull().sum().sum()))

        st.subheader("상위 20행 미리보기")
        st.dataframe(df.head(20), use_container_width=True)

        st.subheader("기본 통계 (숫자형 컬럼)")
        st.dataframe(df.describe(), use_container_width=True)

    # ── 탭 2: 시각화 ──────────────────────────────────────────────────────────
    with tab2:
        # 숫자형 컬럼만 선택 가능하게
        numeric_cols = df.select_dtypes(include="number").columns.tolist()

        if not numeric_cols:
            st.warning("숫자형 데이터가 없어서 차트를 그릴 수 없습니다.")
        else:
            col_to_plot = st.selectbox("📌 차트로 볼 컬럼 선택", numeric_cols)
            chart_type = st.radio(
                "차트 종류",
                ["막대 차트", "라인 차트", "히스토그램"],
                horizontal=True,
            )

            if chart_type == "막대 차트":
                st.bar_chart(df[col_to_plot])

            elif chart_type == "라인 차트":
                st.line_chart(df[col_to_plot])

            else:  # 히스토그램
                fig, ax = plt.subplots()
                ax.hist(df[col_to_plot].dropna(), bins=20, color="steelblue", edgecolor="white")
                ax.set_xlabel(col_to_plot)
                ax.set_ylabel("Count")
                ax.set_title(f"{col_to_plot} Distribution")
                st.pyplot(fig)

    # ── 탭 3: AI 분석 ─────────────────────────────────────────────────────────
    with tab3:
        # LLM에게 넘길 데이터 요약 (전체 데이터 대신 통계 요약만 전달 → 비용 절약)
        data_summary = f"""
- 행 수: {len(df)}
- 열 수: {len(df.columns)}
- 컬럼 목록: {list(df.columns)}
- 기본 통계:
{df.describe().to_string()}
        """.strip()

        # ── AI 전체 분석 버튼 ─────────────────────────────────────────────────
        st.subheader("전체 데이터 분석")
        if st.button("🤖 AI 분석 시작", type="primary"):
            with st.spinner("AI가 데이터를 분석하고 있습니다..."):
                model = load_model()
                response = model.invoke([
                    HumanMessage(content=f"""
다음 데이터를 분석하고 한국어로 인사이트를 제공해주세요.

[데이터 정보]
{data_summary}

아래 형식으로 답변해주세요:
1. **데이터 개요** (2~3문장으로 전체적인 데이터 설명)
2. **주요 특징** (눈에 띄는 특징 3가지)
3. **주의할 점** (데이터 품질 또는 분석 시 유의사항)
""")
                ])
            st.markdown(response.content)

        st.divider()

        # ── 자유 질문 ─────────────────────────────────────────────────────────
        st.subheader("데이터에 대해 질문하기")

        # session_state로 이전 질문/답변 기록 유지
        if "qa_history" not in st.session_state:
            st.session_state.qa_history = []

        # 이전 질문/답변 표시
        for qa in st.session_state.qa_history:
            with st.chat_message("user"):
                st.markdown(qa["question"])
            with st.chat_message("assistant"):
                st.markdown(qa["answer"])

        # 새 질문 입력
        if question := st.chat_input("데이터에 대해 궁금한 점을 물어보세요"):
            with st.chat_message("user"):
                st.markdown(question)

            with st.chat_message("assistant"):
                with st.spinner("답변 생성 중..."):
                    model = load_model()
                    response = model.invoke([
                        HumanMessage(content=f"""
다음 데이터를 바탕으로 질문에 한국어로 답변해주세요.

[데이터 정보]
{data_summary}

[질문]
{question}
""")
                    ])
                st.markdown(response.content)

            # 질문/답변 기록 저장
            st.session_state.qa_history.append({
                "question": question,
                "answer": response.content,
            })

else:
    # 파일 업로드 전 안내 화면
    st.info("위에서 CSV 파일을 업로드하면 분석을 시작합니다.")

    with st.expander("💡 사용 방법"):
        st.markdown("""
1. **CSV 파일 업로드** - 분석하고 싶은 CSV 파일을 드래그하거나 클릭해서 업로드하세요.
2. **📋 데이터 미리보기** - 데이터와 기본 통계를 확인하세요.
3. **📈 시각화** - 원하는 컬럼을 선택해서 차트로 확인하세요.
4. **🤖 AI 분석** - AI 전체 분석을 받거나, 데이터에 대해 자유롭게 질문하세요.
        """)
