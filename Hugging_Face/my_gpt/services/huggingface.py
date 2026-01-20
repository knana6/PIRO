from transformers import pipeline

_generator = pipeline(
    "text-generation",
    model="gpt2",
)

def run_chat_pipeline(messages):
    # 마지막 user만 사용
    last_user = ""
    for m in reversed(messages):
        if m.get("role") == "user":
            last_user = (m.get("content") or "").strip()
            break

    if not last_user:
        return "I didn't get your message."

    prompt = (
        "Answer in English.\n"
        f"Question: {last_user}\n"
        "Answer:"
        # "Pirogramming is a programming club open to anyone interested in learning programming."
    )

    result = _generator(
        prompt,
        max_new_tokens=100,

        # 반복 방지 핵심 3개
        repetition_penalty=1.2,
        no_repeat_ngram_size=4,
        length_penalty=1.05,

        # 디코딩: 너무 뻣뻣하면 반복이 더 생길 때가 있어서
        # 약간만 샘플링(낮은 온도) 추천
        do_sample=True,
        temperature=0.4, #낮을수록 무난한 답변 , 높을수록 편향된?
        top_p=0.9,

        pad_token_id=50256, #시작토큰 
        eos_token_id=50256, # 끝토큰 -> GPT답변이라는 뜻
        return_full_text=True,
    )

    text = result[0]["generated_text"]

    out = text.split("Answer:", 1)[-1].strip()

    # 라벨/반복 컷
    for stop in ["Question:", "User:", "Assistant:", "\n\nQuestion:", "\n\nUser:"]:
        if stop in out:
            out = out.split(stop, 1)[0].strip()

    # 너무 짧거나 비면 fallback
    if not out:
        return "I couldn't generate a good answer."

    return out