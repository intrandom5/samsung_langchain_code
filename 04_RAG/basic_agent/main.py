from agent.agent import agent

def main():
    print("AI : 안녕하세요! 오늘은 무엇을 도와드릴까요?")
    while True:
        user_prompt = input("채팅 (EXIT 입력 시 종료) :")
        if user_prompt.lower() == "exit":
            break
        response = agent.stream(
            {"messages": {"role": "user", "content": user_prompt}},
            {"configurable": {"thread_id": "1"}}
        )

        print(response['messages'][-1].content)
    return

if __name__ == "__main__":
    main()