from typing import Any
from langchain.agents import AgentState
from langchain.agents.middleware import wrap_tool_call, after_agent, before_agent
from langchain_core.messages import AIMessage
from langgraph.runtime import Runtime

_total = {"input": 0, "output": 0}


@wrap_tool_call
def tool_logger(request, handler):
    name = request.tool_call["name"]
    args = request.tool_call["args"]
    print(f"\n  [TOOL] {name} | 인수: {args}")
    result = handler(request)
    print(f"  [TOOL] 결과: {result.content[:100]}...")
    return result


@after_agent
def token_tracker(state: AgentState, runtime: Runtime):
    last = state["messages"][-1]
    if not (hasattr(last, "usage_metadata") and last.usage_metadata):
        return None

    u = last.usage_metadata
    inp = u.get("input_tokens", 0)
    out = u.get("output_tokens", 0)
    _total["input"] += inp
    _total["output"] += out
    print(f"  [TOKEN] 이번: 입력 {inp} / 출력 {out} / 합계 {inp + out}")
    print(f"  [TOKEN] 누적: 입력 {_total['input']} / 출력 {_total['output']} / 합계 {_total['input'] + _total['output']}")
    return None


@before_agent(can_jump_to=["end"])
def guardrail(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    # 순환 참조 방지를 위해 함수 실행 시점에 import합니다
    from .agent import llm

    query = state["messages"][-1].content
    response = llm.invoke(
        f"다음 질문이 키키테크 사내 정보(임직원, 제품, 사내규정 등)와 관련된 질문이면 True, 아니면 False만 답하세요.\n질문: {query}"
    )

    if "true" not in response.content.lower():
        return {
            "messages": [AIMessage(content="죄송합니다. 키키테크 관련 질문에만 답변드릴 수 있습니다.")],
            "jump_to": "end"
        }
    return None
