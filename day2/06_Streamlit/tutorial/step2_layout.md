# Step 2: 레이아웃 구성 — 개념 설명

## 레이아웃이란?

위젯들을 **어디에 배치할지** 결정하는 것입니다.  
Streamlit은 기본적으로 위에서 아래로 쌓이지만(세로 배치),  
레이아웃 요소를 쓰면 가로 배치, 탭 구분, 숨김 처리 등이 가능합니다.

---

## 주요 레이아웃 요소 비교

| 요소 | 용도 | 특징 |
|------|------|------|
| `st.columns()` | 화면을 가로로 분할 | 비율 지정 가능 |
| `st.tabs()` | 내용을 탭으로 구분 | 같은 공간에 여러 내용 |
| `st.sidebar` | 왼쪽 고정 패널 | 설정/필터에 적합 |
| `st.expander()` | 접을 수 있는 섹션 | 보조 정보 숨기기 |
| `st.container()` | 요소를 논리적으로 묶기 | 나중에 내용 채우기 가능 |

---

## st.columns() 패턴

### 균등 분할

```python
col1, col2, col3 = st.columns(3)

with col1:
    st.write("왼쪽")
with col2:
    st.write("가운데")
with col3:
    st.write("오른쪽")
```

### 비율 분할

```python
# 1:2:1 비율 (총 4 기준)
left, main, right = st.columns([1, 2, 1])
```

### with 없이도 사용 가능

```python
col1, col2 = st.columns(2)
col1.write("왼쪽")   # with 대신 .으로 직접 호출
col2.metric("점수", 95)
```

---

## st.sidebar 사용법

```python
# 방법 1: with 블록
with st.sidebar:
    option = st.selectbox("옵션", ["A", "B"])

# 방법 2: 점(.) 접근자
option = st.sidebar.selectbox("옵션", ["A", "B"])
```

두 방법은 동일하게 동작합니다.

---

## 레이아웃 중첩 (Nesting)

레이아웃 요소는 중첩해서 사용할 수 있습니다.

```python
# 탭 안에 컬럼 배치
tab1, tab2 = st.tabs(["탭1", "탭2"])
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.write("탭1의 왼쪽")
    with col2:
        st.write("탭1의 오른쪽")
```

---

## 실전 패턴: 대시보드 레이아웃

```
┌─────────────────────────────────────┐
│ 사이드바 │  상단: 주요 지표 (columns) │
│          │──────────────────────────│
│ 필터     │  중단: 상세 데이터 (tabs) │
│ 설정     │  └ 탭1: 테이블            │
│          │  └ 탭2: 차트              │
│          │──────────────────────────│
│          │  하단: 부가정보 (expander)│
└─────────────────────────────────────┘
```

---

## 다음 단계

레이아웃을 배웠으면, 이제 위젯의 상태를 **기억**하는 방법인  
**Session State**를 배울 차례입니다 → `step3_session_state.py`
