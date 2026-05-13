from langchain.agents.middleware import wrap_tool_call
from langchain.agents.middleware import SummarizationMiddleware, ContextEditingMiddleware, ClearToolUsesEdit

@wrap_tool_call
def logging_middleware(request, handler): # request와 handler 2개의 인자를 반드시 입력 받아야 합니다!
    # request : 도구 호출 정보
    # handler : 실제 도구 실행 함수
    tool_name = request.tool_call["name"] # tool 이름
    tool_args = request.tool_call["args"] # tool의 입력 인자
    print(f"[호출] 도구: {tool_name} | 인수: {tool_args}")
    try:
        result = handler(request)
        print(f"[도구 호출 성공]")
        return result
    except Exception as e:
        print(f"[도구 호출 실패]")
        raise

context_trimmer = ContextEditingMiddleware(
    edits=[
        ClearToolUsesEdit(
            trigger=2000,
            keep=4,
        )
    ]
)

text_summarizer = SummarizationMiddleware(
    model="gpt-5.4-mini",
    trigger=("tokens", 1000),
    keep=("messages", 2)
)