from agent.agent import agent
from agent.middleware import _total


def main():
    print("=" * 50)
    print("🤖 AI 어시스턴트")
    print("=" * 50)
    print("예시 명령어:")
    print("  - '오늘 날짜 알려줘'")
    print("  - '서울 날씨 어때?'")
    print("  - '123 곱하기 456'")
    print("  - '내 이름은 홍길동이야 기억해줘'")
    print("  - '내 정보 불러와줘'")
    print("종료: 'exit' 입력")
    print("=" * 50 + "\n")

    while True:
        user_input = input("나: ").strip()

        if not user_input:
            continue

        if user_input.lower() == "exit":
            print("\n" + "=" * 50)
            print(f"[TOKEN 최종 요약] 입력 {_total['input']} / 출력 {_total['output']} / 합계 {_total['input'] + _total['output']}")
            print("=" * 50)
            print("챗봇을 종료합니다.")
            break

        response = agent.invoke(
            {"messages": {"role": "user", "content": user_input}},
            {"configurable": {"thread_id": "1"}},
        )

        print(f"AI: {response['messages'][-1].content}\n")


if __name__ == "__main__":
    main()
