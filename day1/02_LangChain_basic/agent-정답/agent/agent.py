import os
import uuid
from datetime import date
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

from .tools import get_today_date, get_weather, calculator, save_user_info, load_user_info
from .middleware import logging_middleware, token_tracker

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

credential_key = os.getenv("credential_key")
send_system_name = os.getenv("send_system_name")
model_name = os.getenv("model")
api_base_url = os.getenv("api_base_url")
user_id = os.getenv("user_id")

os.environ["OPENAI_API_KEY"] = "api_key"

llm = ChatOpenAI(
    model=model_name,
    base_url=api_base_url,
    default_headers={
        "x-dep-ticket": credential_key,
        "Send-System-Name": send_system_name,
        "User-Id": user_id,
        "User-Type": "AD_ID",
        "Prompt-Msg-Id": str(uuid.uuid4()),
        "Completion-Msg-Id": str(uuid.uuid4()),
    },
    temperature=0.7,
)

current_dir = os.path.dirname(__file__)
with open(os.path.join(current_dir, "agents.md"), encoding="utf-8") as f:
    system_prompt = f.read()

today_str = date.today().strftime("%Y-%m-%d")
system_prompt = system_prompt.replace("{today}", today_str)

agent = create_agent(
    llm,
    tools=[get_today_date, get_weather, calculator, save_user_info, load_user_info],
    system_prompt=system_prompt,
    middleware=[logging_middleware, token_tracker],
    checkpointer=InMemorySaver(),
)
