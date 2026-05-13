from langchain.tools import tool
from agents import grammer_agent, format_agent, content_agent


@tool
def check_grammer(docs: str) -> str:
    """
    입력 받은 보고서의 문법을 체크하고 피드백합니다.
    """
    result = grammer_agent.invoke({
        "messages": [{"role": "user", "content": docs}]
    })
    return result["messages"][-1].content


@tool
def review_content(docs: str) -> str:
    """
    입력 받은 보고서의 내용을 체크하고 피드백합니다.
    """
    result = format_agent.invoke({
        "messages": [{"role": "user", "content": docs}]
    })
    return result["messages"][-1].content


@tool
def check_format(docs: str) -> str:
    """
    입력 받은 보고서의 형식을 체크하고 피드백합니다.
    """
    result = content_agent.invoke({
        "messages": [{"role": "user", "content": docs}]
    })
    return result["messages"][-1].content