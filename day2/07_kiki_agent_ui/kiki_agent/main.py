from agent.agent import agent
from agent.middleware import _total


def main():
    print("=" * 50)
    print("키키테크 사내 Q&A 챗봇")
    print("=" * 50)
    print("예시 질문:")
    print("  - '이서연 책임의 내선번호가 뭐야?'")
    print("  - 'TalkBridge Enterprise 요금제 알려줘'")
    print("  - '재택근무는 일주일에 몇 번까지 가능해?'")
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
