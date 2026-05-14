import os
import sys
import pandas as pd
from dotenv import load_dotenv, find_dotenv
from langchain_core.tools import tool
from .rag_retriever import RAGRetriever

load_dotenv(find_dotenv())

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

# 제품 관련 문서로 RAGRetriever 구성
product_rag = RAGRetriever()
product_rag.add_file(os.path.join(DATA_DIR, "키키테크_AI솔루션_제품카탈로그.pdf"))
product_rag.add_file(os.path.join(DATA_DIR, "키키테크_회사소개.pptx"))
product_rag.build_retriever()

# 사내 규정 문서로 RAGRetriever 구성
policy_rag = RAGRetriever()
policy_rag.add_file(os.path.join(DATA_DIR, "키키테크_사내규정_행동강령.docx"))
policy_rag.build_retriever()


@tool
def search_employee(name: str) -> str:
    """임직원 이름으로 정보를 검색합니다. 연락처, 부서, 담당업무 등을 확인할 수 있습니다."""
    df = pd.read_excel(os.path.join(DATA_DIR, "키키테크_임직원및프로젝트현황.xlsx"), header=1)
    result = df[df["성명"] == name]

    if result.empty:
        return f"'{name}' 이름의 임직원을 찾을 수 없습니다."

    row = result.iloc[0]
    return "\n".join(f"{col}: {row[col]}" for col in df.columns)


@tool
def search_product(query: str) -> str:
    """키키테크 제품 정보와 회사 소개를 검색합니다."""
    results = product_rag.search(query)
    return "\n\n---\n\n".join(doc.page_content for doc in results)


@tool
def search_policy(query: str) -> str:
    """키키테크 사내 규정과 행동강령을 검색합니다."""
    results = policy_rag.search(query)
    return "\n\n---\n\n".join(doc.page_content for doc in results)
