# ragapp/views.py

# 임포트 & 핑 앤드포인트
import json
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from langchain_upstage import ChatUpstage, UpstageEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate

def ping(request):  
    return HttpResponse("ok")

# 벡터스토어 로드 & 리트리버 구성
VS_DIR = str(settings.BASE_DIR / "vector_store")
_embeddings = UpstageEmbeddings(model="solar-embedding-1-large")  # 인덱싱과 동일
_vectorstore = Chroma(persist_directory=VS_DIR, embedding_function=_embeddings)
_retriever = _vectorstore.as_retriever(
			search_type="mmr", 
			search_kwargs={"k":4,"fetch_k":25,"lambda_mult":0.5}
)

# 프롬프트(역할 지시 + 입력 서식)
SYSTEM = (
    "너는 교육용 한국사 조교야. 주어진 컨텍스트로만 한국어로 간결하게 답해."
    " 모르면 모른다고 말하고, 불확실한 내용은 추측하지 마. 답변은 5문장 이내."
)
prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM),
	    ("human", "질문: {q}\n\n컨텍스트:\n{ctx}") 
	    # 실제 호출할 때 {q},{ctx}에 질문과 검색된 컨텐스트가 들어감
])

# 업스테이지 LLM 준비 (solar-mini는 가성비있는 아이)
llm = ChatUpstage(model="solar-mini", temperature=0)  
# temperature=0은 최대한 일관된 답변을 위해 지정해놓은 것

# 요청 처리부터 응답까지
@csrf_exempt
def ask(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST only")

    # JSON 우선, 폼/쿼리 폴백
    body = {}
    ctype = (request.headers.get("Content-Type") or "").lower()
    if "application/json" in ctype:
        try: body = json.loads(request.body.decode("utf-8"))
        except Exception: body = {}
    if not body:
        body = request.POST.dict() or request.GET.dict()

    q = (body.get("question") or "").strip()
    if not q:
        return HttpResponseBadRequest("question required")

    # Retrieve
    docs = _retriever.invoke(q)
    if not docs:
        return JsonResponse({"answer":"관련 문서를 찾지 못했어요.","sources":[]})

    # 컨텍스트 구성(컨텍스트 길이 제한(문자 약 2500)으로 잘라서 LLM에 넣을 본문을 만듦)
    join_parts, budget = [], 2500
    for d in docs:
        t = (d.page_content or "").strip().replace("\u0000","")
        if not t: continue
        if len("".join(join_parts)) + len(t) > budget:
            t = t[:max(0, budget - len("".join(join_parts)))]
        join_parts.append(t)
        if len("".join(join_parts)) >= budget: break
    ctx = "\n\n".join(join_parts)

    # 프롬프트에 실제 질의/컨텍스트를 넣고 호출 -> 답변 생성함
    messages = prompt.format_messages(q=q, ctx=ctx)
    answer = llm.invoke(messages).content

    # 간단한 요약과 함께 출처 리스트로 반환함
    sources = []
    for d in docs[:3]:
        m = d.metadata or {}
        preview = " ".join((d.page_content or "").split()[:40]) + "..."
        sources.append({"source": m.get("source","PDF"), "page": m.get("page"), "preview": preview})

    return JsonResponse({"answer": answer, "sources": sources})
