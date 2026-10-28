# Ask a 10-K: Project Map

Resume goal: "Measured hallucination on a 30-question golden set, cut it from X% to Y% with reranking and a claim-verification guardrail."

## 1. The system (the "student")

```
PDF -> parse (PyMuPDF) -> chunk (350 words, 60 overlap) -> embed (BGE-small) -> Qdrant
Question -> embed -> top-8 chunks -> Groq LLM -> answer + [source, page N] citations
                                      served by FastAPI, shown in Streamlit
```

Two stages that fail separately:
- **Retrieval**: did the right chunk reach the model?
- **Generation**: did the model read it correctly and cite honestly?

## 2. The evaluation (the "exam")

- `eval/golden_set.json`: 30 questions + expected answer + acceptable PDF pages (the answer key).
  8 Apple, 8 Walmart, 8 JPMorgan, 3 cross-company, 3 unanswerable.
- **Grader 1 (code)** checks WHERE the system looked:
  - `retrieval_hit`: right page in the retrieved chunks
  - `citation_correct`: answer cited an acceptable page
- **Grader 2 (LLM judge)** checks WHAT the system said:
  - answerable: is the answer text correct?
  - unanswerable: did it refuse (no invented figure)?

## 3. Files

| File | Job | Output |
|---|---|---|
| `scripts/ingest_filing.py` | Parse, chunk, embed, store one PDF | Qdrant index |
| `src/generate/answer.py` | `answer_question()`: retrieve + generate | answer + sources |
| `scripts/run_eval.py <label>` | Ask all 30 questions, run Grader 1 | `eval/results/<label>.json` |
| `scripts/judge.py <label>` | Run Grader 2 on saved answers | `eval/results/<label>_judged.json` |
| one-time key-fix script | Repair: added valid pages to the key, fixed citation parser, re-scored | (done, never rerun) |

Run order: `python -m scripts.run_eval baseline` then `python -m scripts.judge baseline`

## 4. Key facts to remember

- Index stores source as `apple_10k` (no `.pdf`). Scorer strips `.pdf` from key names.
- Page numbers are PDF pages, not printed page numbers (Apple offset is +3).
- The same fact appears on several pages, so each question has a LIST of acceptable pages.
- Page checks are not enough: q19 cited the right page and still gave basic EPS ($20.05) instead of diluted ($20.02). That is why the judge exists.
- Unanswerable questions measure hallucination: the correct answer is "can't find it".

## 5. What went wrong and what I fixed (interview story)

1. First run scored 0/27: source-name mismatch in my key. A 0% on a system that visibly works means a broken measurement. I checked one raw result by hand.
2. Re-scored: retrieval 20/27, citation 15/27. I audited all 5 mismatches against the PDF text:
   - citation parser too strict (spaces inside brackets, a zero-width character)
   - answer key missing valid pages (same fact on several pages)
   - one real error (basic vs diluted EPS)
3. Fixed the scorer and the key BEFORE adding the reranker, so before and after use the same ruler.
4. Judge was too strict on 3 questions (graded details the question never asked). Added a rule: grade only what the question asks.

## 6. Baseline status (no reranker, no guardrail)

| Metric | Value | Note |
|---|---|---|
| Retrieval hit | 20/27 | the 7 misses include all 3 cross-company questions |
| Citation correct | 20/27 | after key + parser fixes |
| Answer accuracy (judge) | 17/27 raw | interim: 3 judge-strictness errors being fixed; q20/q21 key being checked |
| Correct refusals | 3/3 | |

Update this table once the judge is rerun. Do not quote the raw 17/27.

## 7. What is left

1. Finish baseline cleanup (judge rule, q20/q21 key check), rerun judge, freeze the baseline.
2. Add `bge-reranker-base` (retrieve ~20, rerank to 8). Rerun exam + judge. Compare.
3. Add claim-verification guardrail. Rerun. Compare.
4. Then: logging, pytest, docker-compose (app + Qdrant), GitHub Actions CI, deployment, README, optional Langfuse.

## 8. Likely interview questions

- Isn't editing the answer key cheating? No. Every added page was checked against the source text, changes were made before the reranker, and both runs use the same key.
- Why not trust the LLM judge blindly? It can be wrong or lenient, so I read its failures against the PDF and spot-check passes. Page matching stays deterministic.
- Why measure retrieval and generation separately? The fixes differ: reranker for retrieval, prompt/guardrail for generation.
- Why can a reranker not fix everything? It only reorders candidates. If the right chunk isn't in the candidate pool, it can't be rescued.
