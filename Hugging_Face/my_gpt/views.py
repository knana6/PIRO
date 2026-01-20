import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

from .models import Conversation, Message
from .services.huggingface import run_chat_pipeline


def main(request):
    conversation = Conversation.objects.create()
    return render(request, "index.html", {"conversation_id": conversation.id})


@csrf_exempt
@require_POST
def chat(request):
    # 1) JSON 파싱 안전 처리
    try:
        body = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "invalid json"}, status=400)

    user_input = (body.get("message") or "").strip()
    conv_id = body.get("conversation_id")

    if not conv_id:
        return JsonResponse({"error": "missing conversation_id"}, status=400)

    if not user_input:
        return JsonResponse({"error": "empty message"}, status=400)

    conversation = get_object_or_404(Conversation, id=conv_id)

    # 2) 사용자 메시지 저장 + 히스토리 구성
    with transaction.atomic():
        Message.objects.create(conversation=conversation, role="user", content=user_input)

        messages = list(
            conversation.messages.order_by("created_at").values("role", "content")
        )

    # 3) HF 호출 실패 대비
    try:
        assistant_reply = run_chat_pipeline(messages)
        assistant_reply = (assistant_reply or "").strip()
        if not assistant_reply:
            assistant_reply = "응답을 생성하지 못했습니다."
    except Exception:
        return JsonResponse({"error": "huggingface_failed"}, status=502)

    # 4) 어시스턴트 메시지 저장
    Message.objects.create(
        conversation=conversation, role="assistant", content=assistant_reply
    )

    return JsonResponse({"reply": assistant_reply})