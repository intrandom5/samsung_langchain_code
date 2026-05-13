# Step 3: Session State — 개념 설명

## Streamlit의 리런(Rerun) 메커니즘

Streamlit을 이해하는 가장 중요한 개념입니다.

### 일반적인 웹 앱 vs Streamlit

**일반 웹 앱 (React, Vue 등)**
```
사용자 조작 → 변경된 부분만 업데이트 → 나머지는 그대로 유지
```

**Streamlit**
```
사용자 조작 → 스크립트 전체를 처음부터 다시 실행 → 화면 전체 재렌더링
```

Streamlit은 매번 전체를 다시 실행하기 때문에, 일반 Python 변수는 초기값으로 돌아갑니다.

---

## 리런이 발생하는 시점

- 위젯(버튼, 슬라이더, 입력창 등)과 사용자가 상호작용할 때
- `st.rerun()`을 코드에서 호출할 때
- 파일이 수정되어 핫 리로드될 때

---

## Session State의 원리

```
┌─────────────────────────────────────────┐
│           Streamlit 앱 실행             │
│                                         │
│  일반 변수: count = 0  ← 리런마다 초기화 │
│                                         │
│  session_state: {     ← 리런해도 유지!  │
│    "count": 5,                          │
│    "name": "홍길동",                    │
│    ...                                  │
│  }                                      │
└─────────────────────────────────────────┘
```

`session_state`는 서버 메모리에 저장되며, **같은 탭** 안에서는 계속 유지됩니다.

---

## 올바른 초기화 패턴

```python
# ❌ 잘못된 방법: 리런할 때마다 덮어씌워짐
st.session_state.count = 0

# ✅ 올바른 방법: 처음 실행 시 없을 때만 초기화
if "count" not in st.session_state:
    st.session_state.count = 0
```

왜 `if "key" not in st.session_state:` 조건이 필요한가?

```
최초 실행: "count" 없음 → 초기화 실행 → count = 0
버튼 클릭 후 리런: "count" = 5 존재 → 초기화 건너뜀 → count = 5 유지
```

---

## st.rerun() 사용 시점

`st.rerun()`은 코드 중간에서 강제로 리런을 발생시킵니다.

```python
if st.button("제출"):
    st.session_state.submitted = True
    st.rerun()  # 즉시 리런해서 UI 변경을 바로 반영

# rerun 후 이 코드가 다시 실행됨
if st.session_state.get("submitted"):
    st.success("제출 완료!")
```

`st.rerun()` 없이 버튼 클릭 후 변경사항을 반영하려면, 다음 사용자 조작을 기다려야 합니다.

---

## 자주 하는 실수

### 실수 1: 초기화 조건문 없이 사용

```python
# ❌ 클릭할 때마다 0으로 초기화됨
st.session_state.count = 0
if st.button("증가"):
    st.session_state.count += 1
```

### 실수 2: 없는 키에 바로 접근

```python
# ❌ 처음 실행 시 "count"가 없으면 KeyError 발생
st.session_state.count += 1

# ✅ get()으로 기본값 지정
st.session_state.count = st.session_state.get("count", 0) + 1
```

### 실수 3: session_state에 저장하지 않고 버튼 결과 유지 시도

```python
# ❌ 버튼을 클릭하면 다음 리런 때 다시 False가 됨
clicked = st.button("클릭")
if clicked:
    st.success("클릭됨!")  # 리런하면 사라짐

# ✅ session_state에 상태 저장
if st.button("클릭"):
    st.session_state.show_success = True
if st.session_state.get("show_success"):
    st.success("클릭됨!")  # 유지됨
```

---

## session_state 생명주기

| 상황 | session_state |
|------|--------------|
| 버튼 클릭 (리런) | 유지 ✅ |
| 슬라이더 조작 (리런) | 유지 ✅ |
| 브라우저 새로고침 (F5) | 초기화 ❌ |
| 새 탭에서 같은 URL 열기 | 각자 독립 세션 |
| 다른 사용자 접속 | 각자 독립 세션 |

---

## 다음 단계

Session State를 이해했으면, 이제 채팅 UI를 만들어봅니다.  
채팅 메시지 기록도 session_state로 관리합니다 → `step4_chat_ui.py`
