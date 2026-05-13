from langchain.agents import AgentState
from langchain.agents.middleware import wrap_tool_call, after_agent
from langgraph.runtime import Runtime

_total = {"input": 0, "output": 0}


@wrap_tool_call
def tool_logger(request, handler):
    name = request.tool_call["name"]
    args = request.tool_call["args"]
    print(f"\n  [TOOL] {name} | 인수: {args}")
    result = handler(request)
    print(f"  [TOOL] 결과: {result.content}")
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
