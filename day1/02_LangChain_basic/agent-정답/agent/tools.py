import os
from datetime import date
from typing import Union

from langchain.tools import tool

MEMORY_PATH = os.path.join(os.path.dirname(__file__), "..", "ai_memory.txt")


@tool
def get_today_date() -> str:
    """오늘의 날짜를 YYYY-MM-DD 형식으로 반환합니다."""
    return date.today().isoformat()


@tool
def get_weather(location: str) -> str:
    """특정 장소의 날씨 정보를 알려주는 기능"""
    return f"It's sunny in {location}"


@tool
def calculator(a: int, b: int, operator: str) -> Union[float, str]:
    """
    2개의 정수 a, b를 입력 받으면 연산자(operator) string에
    해당하는 연산을 수행하고 그 결과를 반환하는 함수.
    operator에는 'plus', 'minus', 'multiply', 'divide' 4가지만 들어갈 수 있다.
    """
    if operator == "plus":
        return a + b
    elif operator == "minus":
        return a - b
    elif operator == "multiply":
        return a * b
    elif operator == "divide":
        if b == 0:
            return "0으로 나눌 수 없습니다."
        return a / b
    else:
        return f"지원하지 않는 연산자입니다: {operator}. 'plus', 'minus', 'multiply', 'divide' 중 하나를 사용하세요."


@tool
def save_user_info(info: str) -> str:
    """사용자에 대한 정보를 기록합니다."""
    with open(MEMORY_PATH, "w", encoding="utf-8") as f:
        f.write(info)
    return "사용자 정보를 저장했습니다."


@tool
def load_user_info() -> str:
    """저장된 사용자 정보를 불러옵니다."""
    try:
        with open(MEMORY_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "저장된 정보가 없습니다."
