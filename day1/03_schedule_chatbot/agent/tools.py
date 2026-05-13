import json
import os
import uuid
from langchain.tools import tool

# schedules.json 파일 경로 (이 파일 기준으로 ../data/schedules.json)
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "schedules.json")


def _load_schedules():
    """JSON 파일에서 일정 목록을 불러옵니다."""
    if not os.path.exists(DATA_PATH):
        return []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_schedules(schedules):
    """일정 목록을 JSON 파일에 저장합니다."""
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(schedules, f, ensure_ascii=False, indent=2)


@tool
def add_schedule(date: str, time: str, title: str, description: str = "") -> str:
    """
    새로운 일정을 추가합니다.
    - date: 날짜 (예: 2024-01-15)
    - time: 시간 (예: 14:00)
    - title: 일정 제목
    - description: 상세 설명 (선택사항)
    """
    schedules = _load_schedules()

    new_schedule = {
        "id": str(uuid.uuid4())[:8],  # 짧은 8자리 ID
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
    - date: 조회할 날짜 (예: 2024-01-15)
    """
    schedules = _load_schedules()

    # 해당 날짜의 일정만 필터링
    day_schedules = [s for s in schedules if s["date"] == date]

    if not day_schedules:
        return f"{date}에 등록된 일정이 없습니다."

    # 시간 순서대로 정렬
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

    # 날짜, 시간 순서대로 정렬
    schedules.sort(key=lambda x: (x["date"], x["time"]))

    result = "[전체 일정]\n"
    current_date = ""
    for s in schedules:
        # 날짜가 바뀔 때마다 날짜 헤더 출력
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

    # ID로 해당 일정 찾기
    target = next((s for s in schedules if s["id"] == schedule_id), None)

    if not target:
        return f"ID '{schedule_id}'에 해당하는 일정을 찾을 수 없습니다. 먼저 일정을 조회해서 ID를 확인해주세요."

    schedules.remove(target)
    _save_schedules(schedules)

    return f"'{target['title']}' 일정이 삭제되었습니다. ({target['date']} {target['time']})"
