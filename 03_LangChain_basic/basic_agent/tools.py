from langchain.tools import tool
from langchain_core.runnables import RunnableConfig
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper


@tool
def calculator(a: int, b: int, operator: str) -> float:
    """
    2개의 정수 a, b를 입력 받으면 연산자(operator) string에 
    해당하는 연산을 수행하고 그 결과를 반환하는 함수.
    operator에는 'plus', 'minus', 'multiply', 'divide' 4가지만 들어갈 수 있다.
    """
    if operator == "plus":
        return a + b
    if operator == "minus":
        return a - b
    if operator == "multiply":
        return a * b
    if operator == "divide":
        return a / b

wikipedia_search = WikipediaQueryRun(
    api_wrapper=WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=500)
)

from langchain_core.runnables import RunnableConfig

@tool
def save_user_info(info: str) -> str:
    """사용자에 대한 정보를 기록합니다. 추후 대화에 도움이 될 만한 사용자 정보를 기록하는데 사용하세요."""
    
    with open(f"user_profile.txt", "w") as f:
        f.write(info)
    
    return "사용자 정보를 저장했습니다."

@tool
def load_user_info() -> str:
    """저장된 사용자 정보를 불러옵니다."""
    
    try:
        with open(f"user_profile.txt", "r") as f:
            return f.read()
    except FileNotFoundError:
        return "저장된 정보가 없습니다."