from langchain.agents import AgentState
from langchain.agents.middleware import wrap_tool_call, after_agent
from langgraph.runtime import Runtime

_total = {"input": 0, "output": 0}


@wrap_tool_call
def logging_middleware(request, handler):
    # TODO: request.tool_call에서 도구 이름과 인수를 꺼내 출력하세요
    # TODO: handler(request)로 도구를 실행하고 결과를 출력한 뒤 반환하세요
    # TODO: 예외 발생 시 오류 내용을 출력하고 다시 raise 하세요
    pass


@after_agent
def token_tracker(state: AgentState, runtime: Runtime):
    # TODO: state["messages"][-1]에서 usage_metadata를 꺼내세요
    # TODO: input_tokens / output_tokens를 _total에 누적하고 출력하세요
    return None
