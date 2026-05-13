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
            # TODO: _total을 이용해 최종 토큰 요약을 출력하세요
            print("챗봇을 종료합니다.")
            break

        # TODO: agent.invoke()로 에이전트를 호출하고 마지막 메시지 내용을 출력하세요


if __name__ == "__main__":
    main()
