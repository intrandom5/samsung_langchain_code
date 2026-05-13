import os
from pathlib import Path
from dotenv import load_dotenv
from middleware import 
from tools import 

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model


def main():
    # 파일을 찾아서 바로 텍스트로 읽어오기
    content = Path("reports.md").read_text(encoding="utf-8")

    # .env 파일로부터 api_key를 불러오는 코드
    load_dotenv(dotenv_path=".env")

    # 모델 이름
    model_name = "gpt-5.4-mini"

    # LLM 정의
    model = init_chat_model(
        model=model_name,
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.7,
    )

    main_agent = create_agent(

    )

    response = main_agent.invoke(
        {"messages": [{"role": "user", "content": content}]}
    )

    print("답변 :\n", response['messages'][-1].content)

if __name__ == "__main__":
    main()