from src.index.embed import embed_query
from src.index.store import get_client, search
from src.generate.llm import generate
from src.generate.prompt import SYSTEM_PROMPT, build_user_prompt

TOP_K = 8


def answer_question(question: str, top_k: int = TOP_K) -> dict:
    client = get_client()
    query_vector = embed_query(question)
    hits = search(client, query_vector, limit=top_k)

    user_prompt = build_user_prompt(question, hits)
    answer_text = generate(SYSTEM_PROMPT, user_prompt)

    sources = [
        {
            "source": h.payload["source"],
            "page": h.payload["page_number"],
            "score": round(h.score, 3),
        }
        for h in hits
    ]

    return {"question": question, "answer": answer_text, "sources": sources}


if __name__ == "__main__":
    import sys
    q = sys.argv[1] if len(sys.argv) > 1 else "What are the main risk factors?"
    result = answer_question(q)
    print("Question:", result["question"])
    print("\nAnswer:\n", result["answer"])
    print("\nSources used:")
    for s in result["sources"]:
        print(f"  {s['source']} page {s['page']} (score {s['score']})")