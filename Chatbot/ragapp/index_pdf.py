# ragapp/index_pdf.py
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter 
from langchain_upstage import UpstageEmbeddings
from langchain_chroma import Chroma  # ← 최신 래퍼
import os

# 경로/환경 준비 
BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

DATA_DIR = BASE_DIR / "data"
VS_DIR = BASE_DIR / "vector_store"

# PDF 로드 & 전처리 
def build_index():
    pdfs = list(DATA_DIR.glob("*.pdf"))
    if not pdfs:
        raise FileNotFoundError(f"data/ 폴더에 PDF가 없습니다 → {DATA_DIR}")

    docs = []
    for pdf in pdfs:
        loader = PyMuPDFLoader(str(pdf))
        d = [x for x in loader.load() if (x.page_content or "").strip()]
        print(f"[load] {pdf.name}: {len(d)} pages with text")
        if d:
            print(" preview:", d[0].page_content[:80].replace("\n"," "), "...")
        docs.extend(d)

# 텍스트 청크 (분할) 
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800, chunk_overlap=120,
        separators=["\n\n","\n"," ",""]
    )
    splits = splitter.split_documents(docs)
    print(f"[split] total chunks: {len(splits)}")

# 임베딩 & 벡터DB에 저장 
    embeddings = UpstageEmbeddings(model="solar-embedding-1-large")
    vs = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory=str(VS_DIR),
    )
    print(f"[done] persisted at: {VS_DIR}")

# 엔트리 포인트: 스크립트를 직접 실행했을 때만 인덱시 수행 
if __name__ == "__main__":
    VS_DIR.mkdir(parents=True, exist_ok=True)
    build_index()