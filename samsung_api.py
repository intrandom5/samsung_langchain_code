from langchain_openai import ChatOpenAI

import os
import uuid
from dotenv import load_dotenv


load_dotenv("../.env")

credential_key=os.getenv("credential_key")
send_system_name=os.getenv("send_system_name")
model_name=os.getenv("model")
api_base_url=os.getenv("api_base_url")
user_id=os.getenv("user_id")

os.environ["OPENAI_API_KEY"] = 'api_key'

llm = ChatOpenAI(
    model=model_name,
    base_url=api_base_url,
    default_headers={
        'x-dep-ticket': credential_key,
        'Send-System-Name': send_system_name,
        'User-Id': user_id,
        'User-Type': "AD_ID",
        'Prompt-Msg-Id': str(uuid.uuid4()),
        'Completion-Msg-Id': str(uuid.uuid4())
    },
    temperature=0.7,
)

from langchain.agents.middleware import SummarizationMiddleware

text_summarizer = SummarizationMiddleware(
    model=llm,
    base_url=api_base_url,
    default_headers={
        'x-dep-ticket': credential_key,
        'Send-System-Name': send_system_name,
        'User-Id': user_id,
        'User-Type': "AD_ID",
        'Prompt-Msg-Id': str(uuid.uuid4()),
        'Completion-Msg-Id': str(uuid.uuid4())
    },
    trigger=("tokens", 1000),
    keep=("messages", 2)
)