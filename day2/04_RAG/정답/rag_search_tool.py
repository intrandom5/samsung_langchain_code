from pathlib import Path
from rag_retriever import RAGRetriever
from langchain_core.tools import tool

# 1. 사람이 직접 설정 (agent 실행 전 1회)
rag = RAGRetriever()
rag.add_file("data/키키테크_임직원및프로젝트현황.xlsx")
rag.add_file("data/키키테크_AI솔루션_제품카탈로그.pdf")
rag.add_file("data/키키테크_사내규정_행동강령.docx")
rag.add_file("data/키키테크_회사소개.pptx")
rag.build_retriever(sparse_weight=0.4, dense_weight=0.6, k=5)

# 2. search 메서드만 tool로 감싸기
@tool
def search_documents(query: str) -> str:
    """VectorDB에서 문서를 검색합니다. 키키테크의 제품 정보, 사내 규정, 임직원 및 프로젝트 현황 등의 정보를 확인할 수 있습니다."""
    results = rag.search(query)
    formatted = []
    for doc in results:
        source = Path(doc.metadata.get("source", "unknown")).name
        formatted.append(f"[출처: {source}]\n{doc.page_content}")
    return "\n\n---\n\n".join(formatted)

# 3. agent에 tool로 전달