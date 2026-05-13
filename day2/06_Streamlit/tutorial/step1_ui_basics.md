# Step 1: Streamlit UI 기초 — 개념 설명

## Streamlit의 실행 원리 (가장 중요!)

Streamlit을 처음 배울 때 **반드시** 이해해야 하는 핵심 동작 방식이 있습니다.

### "리런(Rerun)" 메커니즘

```
사용자가 버튼 클릭, 텍스트 입력, 슬라이더 조작 등을 하면
         ↓
Streamlit이 이 스크립트 전체를 위→아래로 처음부터 다시 실행
         ↓
화면을 새로운 실행 결과로 업데이트
```

이것을 **리런(rerun)** 이라고 합니다.

#### 예시로 이해하기

```python
import streamlit as st

count = 0  # 리런할 때마다 이 줄이 실행 → 항상 0으로 초기화!

if st.button("클릭"):
    count += 1  # count가 0이라 1이 되지만...

st.write(count)  # 항상 1만 표시됨 (0+1)
```

위 코드에서 버튼을 아무리 눌러도 `1`만 표시됩니다.  
리런할 때마다 `count = 0`이 실행되기 때문입니다.

→ 이 문제의 해결책이 **Session State** (Step 3에서 다룹니다)

---

## 위젯의 반환값

Streamlit의 모든 입력 위젯은 **현재 상태의 값을 반환**합니다.

| 위젯 | 반환 타입 | 초기값 |
|------|----------|--------|
| `st.text_input()` | `str` | `""` (빈 문자열) |
| `st.number_input()` | `int` 또는 `float` | `value` 파라미터 |
| `st.checkbox()` | `bool` | `False` |
| `st.button()` | `bool` | `False` (클릭 시 한 번만 `True`) |
| `st.selectbox()` | 선택된 항목 | `options[index]` |
| `st.multiselect()` | `list` | `default` 파라미터 |
| `st.slider()` | `int` 또는 `float` | `value` 파라미터 |
| `st.date_input()` | `datetime.date` | 오늘 날짜 |

```python
# 반환값 활용 예시
name = st.text_input("이름")   # 현재 입력된 문자열
age  = st.number_input("나이") # 현재 선택된 숫자

# 입력이 있을 때만 처리
if name:  # 빈 문자열은 False → 입력이 없으면 이 블록 실행 안 됨
    st.write(f"안녕하세요, {name}님! 나이: {age}세")
```

---

## 자주 쓰는 위젯 한눈에 보기

### 텍스트 출력

```python
st.title("제목")          # 가장 큰 제목
st.header("헤더")         # 섹션 제목
st.subheader("서브헤더")  # 소제목
st.write("내용")          # 범용 출력 (뭐든 출력 가능)
st.markdown("**굵게**")   # 마크다운 지원
st.caption("작은 글씨")   # 부가 설명
st.code("print('hi')")    # 코드 블록
st.divider()              # 구분선
```

### 사용자 입력

```python
name  = st.text_input("이름")
bio   = st.text_area("소개")
num   = st.number_input("숫자", min_value=0, max_value=100)
level = st.slider("레벨", 1, 10)
opt   = st.selectbox("선택", ["A", "B", "C"])
opts  = st.multiselect("다중선택", ["A", "B", "C"])
radio = st.radio("라디오", ["A", "B"])
check = st.checkbox("동의")
date  = st.date_input("날짜")
```

### 피드백

```python
st.success("성공 메시지")
st.info("정보 메시지")
st.warning("경고 메시지")
st.error("오류 메시지")
st.toast("우상단 알림")    # 잠깐 표시됐다 사라짐
st.balloons()              # 풍선 효과 🎉
st.snow()                  # 눈 내리기 효과 ❄️
```

### 데이터 표시

```python
st.dataframe(df)           # 인터랙티브 데이터프레임
st.table(df)               # 정적 표
st.metric("매출", "₩100만", delta="+10%")
st.json({"key": "value"})  # JSON 뷰어
```

---

## 다음 단계

`step1_ui_basics.py`에서 각 위젯을 직접 조작해보고 나면,  
`step2_layout.py`로 넘어가서 이 위젯들을 **어떻게 배치**할지 배웁니다.
