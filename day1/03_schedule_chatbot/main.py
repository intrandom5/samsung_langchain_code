from agent.agent import agent

def main():
    print("=" * 50)
    print("📅 일정 관리 챗봇")
    print("=" * 50)
    print("예시 명령어:")
    print("  - '내일 오후 3시에 팀 미팅 추가해줘'")
    print("  - '이번 주 일정 전부 보여줘'")
    print("  - '2025-05-15 일정 알려줘'")
    print("  - '팀 미팅 삭제해줘'")
    print("종료: 'exit' 입력")
    print("=" * 50 + "\n")

    while True:
        user_input = input("나: ").strip()

        # 빈 입력 무시
        if not user_input:
            continue

        # 종료
        if user_input.lower() == "exit":
            print("챗봇을 종료합니다.")
            break

        # 에이전트 호출 (thread_id="1"로 대화 이어가기)
        response = agent.invoke(
            {"messages": {"role": "user", "content": user_input}},
            {"configurable": {"thread_id": "1"}},
        )

        print(f"AI: {response['messages'][-1].content}\n")


if __name__ == "__main__":
    main()
