"""
스케줄 관리 도구 모음
=====================
day1/03_schedule_chatbot/agent/tools.py를 그대로 재활용합니다.
변경 사항: DATA_PATH만 이 프로젝트의 data/ 폴더를 가리키도록 수정

도구 목록:
    - add_schedule    : 일정 추가
    - get_schedules   : 특정 날짜 일정 조회
    - list_all_schedules : 전체 일정 조회
    - delete_schedule : 일정 삭제
"""
import json
import os
import uuid

from langchain.tools import tool

# 이 파일(schedule_tools.py)이 있는 위치: day2/02_work_assistant/tools/
# 데이터 파일 위치:                        day2/02_work_assistant/data/schedules.json
# 즉, 한 단계 위로(..)올라간 뒤 data/ 폴더로 들어가면 됩니다.
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "schedules.json")


def _load_schedules() -> list:
    """JSON 파일에서 일정 목록을 불러옵니다. 파일이 없으면 빈 리스트를 반환합니다."""
    if not os.path.exists(DATA_PATH):
        return []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_schedules(schedules: list) -> None:
    """일정 목록을 JSON 파일에 저장합니다."""
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(schedules, f, ensure_ascii=False, indent=2)


@tool
def add_schedule(date: str, time: str, title: str, description: str = "") -> str:
    """
    새로운 일정을 추가합니다.
    - date: 날짜 (YYYY-MM-DD 형식, 예: 2024-01-15)
    - time: 시간 (HH:MM 형식, 예: 14:00)
    - title: 일정 제목
    - description: 상세 설명 (선택사항)
    """
    schedules = _load_schedules()

    new_schedule = {
        "id": str(uuid.uuid4())[:8],
        "date": date,
        "time": time,
        "title": title,
        "description": description,
    }

    schedules.append(new_schedule)
    _save_schedules(schedules)

    return f"일정이 추가되었습니다! (ID: {new_schedule['id']}) {date} {time} - {title}"


@tool
def get_schedules(date: str) -> str:
    """
    특정 날짜의 일정을 조회합니다.
    - date: 조회할 날짜 (YYYY-MM-DD 형식, 예: 2024-01-15)
    """
    schedules = _load_schedules()
    day_schedules = [s for s in schedules if s["date"] == date]

    if not day_schedules:
        return f"{date}에 등록된 일정이 없습니다."

    day_schedules.sort(key=lambda x: x["time"])

    result = f"[{date} 일정 목록]\n"
    for s in day_schedules:
        result += f"- {s['time']} {s['title']}"
        if s["description"]:
            result += f" ({s['description']})"
        result += f" [ID: {s['id']}]\n"

    return result


@tool
def list_all_schedules() -> str:
    """저장된 모든 일정을 날짜 순서대로 조회합니다."""
    schedules = _load_schedules()

    if not schedules:
        return "저장된 일정이 없습니다."

    schedules.sort(key=lambda x: (x["date"], x["time"]))

    result = "[전체 일정]\n"
    current_date = ""
    for s in schedules:
        if s["date"] != current_date:
            current_date = s["date"]
            result += f"\n📅 {current_date}\n"
        result += f"  - {s['time']} {s['title']}"
        if s["description"]:
            result += f" ({s['description']})"
        result += f" [ID: {s['id']}]\n"

    return result


@tool
def delete_schedule(schedule_id: str) -> str:
    """
    일정을 삭제합니다.
    - schedule_id: 삭제할 일정의 ID (일정 조회 시 확인 가능)
    """
    schedules = _load_schedules()
    target = next((s for s in schedules if s["id"] == schedule_id), None)

    if not target:
        return f"ID '{schedule_id}'에 해당하는 일정을 찾을 수 없습니다. 먼저 일정을 조회해서 ID를 확인해주세요."

    schedules.remove(target)
    _save_schedules(schedules)

    return f"'{target['title']}' 일정이 삭제되었습니다. ({target['date']} {target['time']})"
