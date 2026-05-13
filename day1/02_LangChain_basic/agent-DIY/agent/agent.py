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

# TODO: 환경변수에서 credential_key, send_system_name, model, api_base_url, user_id를 가져오세요

os.environ["OPENAI_API_KEY"] = "api_key"

# TODO: ChatOpenAI 모델을 생성하세요
# model, base_url, default_headers(x-dep-ticekt, Send-System-Name, User-Id, User-Type, Prompt-Msg-Id, Completion-Msg-Id), temperature=0.7

# TODO: agents.md 파일을 읽어 system_prompt에 저장하세요
# TODO: system_prompt의 {today}를 오늘 날짜로 치환하세요

# TODO: create_agent()로 에이전트를 생성하세요
# tools, system_prompt, middleware, checkpointer 모두 포함
agent = None
