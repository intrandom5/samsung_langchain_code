import os
from datetime import date
from typing import Union

from langchain.tools import tool

MEMORY_PATH = os.path.join(os.path.dirname(__file__), "..", "ai_memory.txt")


@tool
def get_today_date() -> str:
    """오늘의 날짜를 YYYY-MM-DD 형식으로 반환합니다."""
    # TODO: 오늘 날짜를 isoformat()으로 반환하세요


@tool
def get_weather(location: str) -> str:
    """특정 장소의 날씨 정보를 알려주는 기능"""
    # TODO: "{location}의 날씨는 맑습니다" 형태의 문자열을 반환하세요


@tool
def calculator(a: int, b: int, operator: str) -> Union[float, str]:
    """
    2개의 정수 a, b를 입력 받으면 연산자(operator) string에
    해당하는 연산을 수행하고 그 결과를 반환하는 함수.
    operator에는 'plus', 'minus', 'multiply', 'divide' 4가지만 들어갈 수 있다.
    """
    # TODO: operator에 따라 사칙연산을 수행하고 결과를 반환하세요
    # divide의 경우 0으로 나누는 예외 처리도 포함하세요


@tool
def save_user_info(info: str) -> str:
    """사용자에 대한 정보를 기록합니다."""
    # TODO: MEMORY_PATH 파일에 info를 저장하고 완료 메시지를 반환하세요


@tool
def load_user_info() -> str:
    """저장된 사용자 정보를 불러옵니다."""
    # TODO: MEMORY_PATH 파일을 읽어 반환하세요
    # 파일이 없을 경우 "저장된 정보가 없습니다."를 반환하세요
