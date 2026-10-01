SYSTEM_PROMPT = """You are a financial analyst assistant. You answer questions about \
SEC 10-K filings using ONLY the excerpts provided to you below. Follow these rules \
strictly:

1. Base your answer only on the provided excerpts. Do not use outside knowledge.
2. Every factual claim must end with a citation using square brackets, in exactly \
this format: [source, page X]. For example: "Revenue grew 5% [apple_10k, page 29]." \
Do not use any other bracket style.
3. If the excerpts do not contain enough information to answer the question, say so \
explicitly instead of guessing.
4. Be concise and direct."""


def build_user_prompt(question: str, chunks) -> str:
    excerpt_blocks = []
    for c in chunks:
        block = f"[{c.payload['source']}, page {c.payload['page_number']}]\n{c.payload['text']}"
        excerpt_blocks.append(block)

    excerpts_text = "\n\n---\n\n".join(excerpt_blocks)

    return f"""Question: {question}

Excerpts:
{excerpts_text}

Answer the question using only the excerpts above, citing sources as instructed."""